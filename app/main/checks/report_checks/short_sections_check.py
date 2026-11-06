import re

from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportShortSectionsCheck(BaseReportCriterion):
    label = 'Поиск коротких разделов в отчёте'
    _description = 'Минимальное число текстовых абзацев и слов в разделе с учётом подразделов.'
    id = 'short_sections_check'

    def __init__(
        self,
        file_info,
        min_section_count=5,
        min_section_len=20,
        main_heading_style=None,
        prechecked_props=StyleCheckSettings.PRECHECKED_PROPS,
    ):
        super().__init__(file_info)
        self.min_section_count = min_section_count
        self.min_section_len = min_section_len
        self.main_heading_style = (
            main_heading_style or ('heading 3' if self.file_type['report_type'] == 'LR' else 'heading 2')
        ).lower()

    def check(self):
        chapters = self.file.make_chapters(self.file_type['report_type'])
        selected = [(i, chapter) for i, chapter in enumerate(chapters) if chapter['style'] == self.main_heading_style]
        if not selected:
            return answer(False, 'Не найдено ни одного заголовка требуемого уровня.')
        errors = []
        for index, chapter in selected:
            if 'приложение' in chapter['text'].lower():
                break
            children = list(chapter['child'])
            level = int(chapter['style'].split()[-1])
            for nested in chapters[index + 1 :]:
                if int(nested['style'].split()[-1]) <= level:
                    break
                children.extend(nested['child'])
            texts = [
                child['text']
                for child in children
                if child['text'].strip()
                and not any(marker in child['style'] for marker in ('подпись', 'md_table', 'листинг'))
            ]
            words = len(re.findall(r'\w+', ' '.join(texts)))
            if len(texts) < self.min_section_count or words < self.min_section_len:
                errors.append(
                    f'Раздел "{chapter["text"]}" содержит {len(texts)} абзацев и {words} слов; '
                    f'требуется не менее {self.min_section_count} абзацев и {self.min_section_len} слов.'
                )
        return answer(not errors, '<br>'.join(errors) or 'Все разделы достигают рекомендуемой длины.')
