import re

from ..base_check import BaseReportCriterion, answer


class ReportParagraphsCountCheck(BaseReportCriterion):
    label = 'Проверка количества абзацев в главах и их подразделах'
    _description = 'Количество текстовых абзацев с учётом вложенных подразделов.'
    id = 'paragraphs_count_check'

    def __init__(
        self,
        file_info,
        min_paragraphs_in_unnumbered_section=2,
        min_paragraphs_in_section=5,
        min_paragraphs_in_subsection=5,
        min_paragraphs_in_subsubsection=1,
        skip_sections=None,
    ):
        super().__init__(file_info)
        self.minimums = (
            min_paragraphs_in_unnumbered_section,
            min_paragraphs_in_section,
            min_paragraphs_in_subsection,
            min_paragraphs_in_subsubsection,
        )
        self.skip_sections = [name.lower() for name in (skip_sections or [])]

    def check(self):
        chapters = self.file.make_chapters(self.file_type['report_type'])
        if not chapters:
            return answer(False, 'Не найдено ни одного заголовка.')
        errors = []
        for index, chapter in enumerate(chapters):
            name = chapter['text']
            if name.lower().startswith('приложение'):
                break
            if any(skip in name.lower() for skip in self.skip_sections):
                continue
            level = int(chapter['style'].split()[-1])
            minimum_index = 0 if not re.match(r'\d', name) else min(max(level - 1, 1), 3)
            children = list(chapter['child'])
            for nested in chapters[index + 1 :]:
                if int(nested['style'].split()[-1]) <= level:
                    break
                children.extend(nested['child'])
            count = sum(
                bool(child['text'].strip())
                and not any(marker in child['style'] for marker in ('подпись', 'md_table', 'листинг'))
                for child in children
            )
            minimum = self.minimums[minimum_index]
            if count < minimum:
                errors.append(f'Раздел "{name}" содержит {count} абзацев; требуется не менее {minimum}.')
        return answer(not errors, '<br>'.join(errors) or 'Пройдена!')
