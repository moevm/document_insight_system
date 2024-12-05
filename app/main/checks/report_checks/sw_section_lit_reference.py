import re

from logging import getLogger

from ..base_check import BaseReportCriterion, answer


logger = getLogger('root')

SW_CONSTANTS = {
    "SW_KEY_QUESTIONS_SECTIONS": {
        "Актуальность": {
            "count": 1
        }
    },
    "SW_ANALOGS_SECTIONS": {
        "Принцип отбора аналогов": {
            "count": 4,
            "subchapters": 1
        }
    },
    "SW_FINAL_SECTIONS": {
        "Введение": {
            "count": 1
        },
        "Обзор предметной области": {
            "count": 4,
            "subchapters": 1
        },
        
    },
}


class SWSectionLiteratureReferenceCheck(BaseReportCriterion):
    label = "Проверка наличия ссылок на литературу в определенных разделах"
    description = "Проверка наличия и количества ссылок на литературу в определенных разделах"
    id = "sw_section_lit_reference"
    priority = True

    def __init__(self, file_info, sections_info=None):
        super().__init__(file_info)

        self.sections = None
        if sections_info in SW_CONSTANTS:
            self.sections = SW_CONSTANTS[sections_info]
        elif isinstance(sections_info, dict):
            self.sections = sections_info

    def check(self):
        self.file.make_chapters('VKR')
        chapters = self.file.chapters_to_str()
        chapter_tree = self.file.build_chapter_tree(chapters)
        result = dict.fromkeys(self.sections.keys(), None)
        feedback = ""

        for chapter in chapters:
            if chapter['name'] in self.sections:
                subchapter_settings = self.sections[chapter['name']].get("subchapters")
                main_chapter_references = len(
                    self.search_references(chapter['text'])[0])
                subchapter_result = []

                if chapter['node'].get('children'):
                    for subchapter in chapter['node']['children']:
                        subchapter_references = len(
                            self.search_references(subchapter['text'])[0])
                        main_chapter_references += subchapter_references

                        # check count_ref of subchapter
                        subchapter_result.append({
                            "name": subchapter['name'],
                            "count": subchapter_references
                        })

                # CHECK1: verify chapter count references
                verify_count_references = main_chapter_references >= self.sections[chapter['name']]['count']
                result[chapter['name']] = {
                    "count": verify_count_references
                }
                if not verify_count_references:
                    feedback += f"<br> Раздел '{chapter['name']}' содержит недостаточное количество ссылок на источники. " \
                        f"Сейчас их {main_chapter_references}, должно быть не менее {self.sections[chapter['name']]['count']}"

                # CHECK2: verify subchapter count references
                if subchapter_settings:
                    verify_subchapter_references = all(subchapter['count']>=subchapter_settings for subchapter in subchapter_result)
                    result[chapter['name']]['subchapters'] = verify_subchapter_references
                    if not verify_subchapter_references:
                        feedback += f"<br> Каждый из подразделов (уровень вложенности +1) раздела '{chapter['name']}' должен содержать не менее {self.sections[chapter['name']]['subchapters']} ссылок на источники. " \
                            f"Сейчас их: {', '.join(subchapter['name'] + ' - ' + str(subchapter['count']) for subchapter in subchapter_result)}"
        if feedback:
            return answer(0, feedback)

        return answer(1, "Проверка пройдена!")

    def search_references(self, chapter_text):
        """
        Re-worked ReferencesToLiteratureCheck.search_references
        """
        prev_ref, ref_sequence, array_of_references = 0, [], set()
        detected_references = re.findall(r'\[[\d \-,]+\]', chapter_text)
        for reference in detected_references:
            for one_part in re.split(r'[\[\],]', reference):
                if re.match(r'\d+[ \-]+\d+', one_part):
                    start, end = re.split(r'[ -]+', one_part)
                    for k in range(int(start), int(end) + 1):
                        prev_ref = self.add_references(
                            k, prev_ref, array_of_references, ref_sequence)
                elif one_part:
                    prev_ref = self.add_references(
                        int(one_part), prev_ref, array_of_references, ref_sequence)
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
