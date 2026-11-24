import re

from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph

from ...reports.section_patterns import CONTENTS_STYLE_PATTERN, CONTENTS_TITLE
from ..base_check import BaseReportCriterion, answer


class ReportRightWordsCheck(BaseReportCriterion):
    label = "Проверка наличия определенных (правильных) слов в тексте отчёта"
    _description = ''
    id = 'right_words_check'

    def __init__(self, file_info, patterns=("цел[ьией]",)):
        super().__init__(file_info)
        self.patterns = dict.fromkeys(patterns, False)
        self.warning = not bool(self.patterns)

    def texts_without_contents(self):
        if self.is_markdown:
            yield from self.file.pdf_file.get_text_on_page().values()
            return
        in_contents = False
        for block in self.file.file.element.body:
            if block.tag == qn('w:p'):
                paragraph = Paragraph(block, self.file.file)
                style = paragraph.style.name.lower()
                text = paragraph.text
                if re.fullmatch(CONTENTS_STYLE_PATTERN, style):
                    continue
                if text.strip().casefold() == CONTENTS_TITLE.casefold():
                    in_contents = True
                    continue
                if in_contents and style.startswith('heading '):
                    in_contents = False
            else:
                text = ' '.join(node.text or '' for node in block.iter(qn('w:t')))
            if not in_contents:
                yield text

    def check(self):
        if not self.patterns:
            return answer(True, 'Шаблоны поиска не заданы; критерий не влияет на оценку.')
        if not self.has_enough_pages():
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.patterns = dict.fromkeys(self.patterns, False)
        for text_on_page in self.texts_without_contents():
            lower_text = text_on_page.lower()
            for pattern in self.patterns:
                if re.search(pattern, lower_text, re.I):
                    self.patterns[pattern] = True
        result_score = 0
        if all(value for value in self.patterns.values()):
            result_score = 1
        if result_score:
            return answer(result_score, "Пройдена!")
        else:
            result_str = '</li><li>'.join([k for k, v in self.patterns.items() if not v])
            return answer(
                result_score,
                f'Не найдены слова, соответствующие следующим регулярным выражениям: <ul><li>{result_str}</ul>',
            )
