from copy import deepcopy
from logging import getLogger

from ..base_check import BaseReportCriterion, answer
from ..references import literature_numbers

logger = getLogger('root')

SW_CONSTANTS = {
    "SW_KEY_QUESTIONS_SECTIONS": {"Актуальность": {"count": 1}},
    "SW_ANALOGS_SECTIONS": {"Принцип отбора аналогов": {"count": 4, "subchapters": 1}},
    "SW_FINAL_SECTIONS": {
        "Введение": {"count": 1},
        "Принцип отбора аналогов": {"count": 4, "subchapters": 1},
    },
}


class SWSectionLiteratureReferenceCheck(BaseReportCriterion):
    label = "Проверка наличия ссылок на литературу в определенных разделах"
    _description = "Проверка наличия и количества ссылок на литературу в определенных разделах"
    id = "sw_section_lit_reference"
    priority = True

    def __init__(self, file_info, sections_info=None):
        super().__init__(file_info)

        if sections_info is None:
            sections_info = 'SW_KEY_QUESTIONS_SECTIONS'
        if isinstance(sections_info, dict):
            self.sections = deepcopy(sections_info)
        elif isinstance(sections_info, str) and sections_info in SW_CONSTANTS:
            self.sections = deepcopy(SW_CONSTANTS[sections_info])
        else:
            raise ValueError(f'Неизвестная конфигурация разделов: {sections_info!r}')

        self.warning = not bool(self.sections)

    def check(self):
        if not self.sections:
            return answer(True, 'Правила для выбранных разделов не заданы; критерий не влияет на оценку.')
        if not self.is_markdown:
            return answer(False, 'Критерий предназначен для отчётов Markdown.')
        self.file.make_chapters('VKR')
        chapters = self.file.chapters_to_str()
        _ = self.file.build_chapter_tree(chapters)  # TODO: use tree

        def references_in_node(node):
            numbers = self.search_references(node['text'])[0]
            for child in node.get('children', []):
                numbers.update(references_in_node(child))
            return numbers

        result = dict.fromkeys(self.sections.keys(), None)
        feedback = ""

        for chapter in chapters:
            if chapter['name'] in self.sections:
                subchapter_settings = self.sections[chapter['name']].get("subchapters")
                main_references = self.search_references(chapter['text'])[0]
                subchapter_result = []

                if chapter['node'].get('children'):
                    for subchapter in chapter['node']['children']:
                        subchapter_numbers = references_in_node(subchapter)
                        subchapter_references = len(subchapter_numbers)
                        main_references.update(subchapter_numbers)

                        # check count_ref of subchapter
                        subchapter_result.append({"name": subchapter['name'], "count": subchapter_references})

                main_chapter_references = len(main_references)
                # CHECK1: verify chapter count references
                verify_count_references = main_chapter_references >= self.sections[chapter['name']]['count']
                result[chapter['name']] = {"count": verify_count_references}
                if not verify_count_references:
                    feedback += (
                        f"<br> Раздел '{chapter['name']}' содержит недостаточное количество ссылок на источники. "
                        f"Сейчас их {main_chapter_references}, должно быть не менее "
                        f"{self.sections[chapter['name']]['count']}"
                    )

                # CHECK2: verify subchapter count references
                if subchapter_settings:
                    verify_subchapter_references = all(
                        subchapter['count'] >= subchapter_settings for subchapter in subchapter_result
                    )
                    result[chapter['name']]['subchapters'] = verify_subchapter_references
                    if not verify_subchapter_references:
                        feedback += (
                            f"<br> Каждый из подразделов (уровень вложенности +1) раздела '{chapter['name']}'"
                            f"должен содержать не менее {self.sections[chapter['name']]['subchapters']} "
                            f"ссылок на источники. Сейчас их: "
                            f"{', '.join(sc['name'] + ' - ' + str(sc['count']) for sc in subchapter_result)}"
                        )
        missing = [name for name, value in result.items() if value is None]
        if missing:
            feedback += '<br>Не найдены разделы: ' + ', '.join(missing)
        if feedback:
            return answer(0, feedback)

        return answer(1, "Проверка пройдена!")

    def search_references(self, chapter_text):
        """
        Re-worked ReferencesToLiteratureCheck.search_references
        """
        prev_ref, ref_sequence, array_of_references = 0, [], set()
        for number in literature_numbers(chapter_text):
            prev_ref = self.add_references(number, prev_ref, array_of_references, ref_sequence)
        if ref_sequence:
            if ref_sequence[0][1] == '0':
                ref_sequence[0] = ref_sequence[0].replace('[0],', '')
        return array_of_references, ref_sequence

    def add_references(self, k, prev_ref, array_of_references, ref_sequence):
        if k not in array_of_references:
            if k - prev_ref != 1:
                ref_sequence.append(f'[{prev_ref}], [{k}]')
            prev_ref = k
        elif k - prev_ref == 1:
            prev_ref = k
        array_of_references.add(k)
        return prev_ref
