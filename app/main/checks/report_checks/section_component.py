from ..base_check import BaseReportCriterion, answer
from .section_component_config import SECTION_CONFIG
from .style_check_settings import StyleCheckSettings


class ReportSectionComponent(BaseReportCriterion):
    label = "Проверка наличия необходимых компонентов указанного раздела и их форматирования"
    _description = "Проверка наличия необходимых компонентов раздела и форматирования (жирный шрифт)"
    id = 'report_section_component'

    def __init__(
        self,
        file_info,
        chapter='Введение',
        patterns=None,
        bold_check_exceptions=None,
        headers_map=None,
        check_bold=True,
    ):
        super().__init__(file_info)
        if not isinstance(check_bold, bool):
            raise ValueError('check_bold должен быть логическим значением true или false.')
        self.check_bold = check_bold
        if not check_bold:
            self.label = 'Проверка наличия необходимых компонентов указанного раздела'
        self.intro = {}

        # конфиг
        chapter_lower = chapter.lower()

        if chapter_lower in SECTION_CONFIG:
            section_config = SECTION_CONFIG[chapter_lower]
        else:
            section_config = SECTION_CONFIG['default']

        if patterns is None:
            patterns = section_config['patterns']

        if bold_check_exceptions is None:
            bold_check_exceptions = section_config['bold_check_exceptions']

        self.bold_check_exceptions = [txt.lower() for txt in bold_check_exceptions]

        if headers_map:
            self.config = headers_map
            self.chapter = ''
        else:
            self.chapter = chapter

        self.chapters = []
        self.patterns = []
        for pattern in patterns:
            self.patterns.append({"name": pattern.capitalize(), "text": pattern, "marker": 0, "paragraph_index": None})

    def late_init(self):
        if not self.chapter:
            self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
            if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config, {}):
                self.chapter = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main][
                    "header_for_report_section_component"
                ]
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def _is_text_bold_in_paragraph(self, paragraph, search_text):
        text = ''.join(run['text'] for run in paragraph.get('runs', []))
        offset = text.lower().find(search_text.lower())
        if offset < 0:
            return False
        end, position = offset + len(search_text), 0
        for run in paragraph.get('runs', []):
            run_end = position + len(run['text'])
            if position < end and run_end > offset and not getattr(run.get('style'), 'bold', False):
                return False
            position = run_end
        return True

    def _check_bold_formatting(self, pattern):
        text_to_check = pattern['text'].lower()

        if text_to_check in self.bold_check_exceptions:
            return True

        if pattern['paragraph_index'] is None:
            return False

        if pattern['paragraph_index'] < len(self.file.styled_paragraphs):
            paragraph = self.file.styled_paragraphs[pattern['paragraph_index']]
            return self._is_text_bold_in_paragraph(paragraph, pattern['text'])

        return False

    def check(self):
        if not self.has_enough_pages():
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")

        for pattern in self.patterns:
            pattern['marker'] = 0
            pattern['paragraph_index'] = None
        self.late_init()
        if not self.chapter:
            return answer(True, f'Данная проверка не предусмотрена для работы с темой "{self.headers_main}"')

        self.intro = {}
        for intro in self.chapters:
            header = intro["text"].lower()
            if header.find(self.chapter.lower()) >= 0:
                self.intro = intro
                break

        if not self.intro:
            return answer(False, f'Раздел "{self.chapter}" не обнаружен!')

        # проверка наличия компонент
        for intro_par in self.intro["child"]:
            par = intro_par["text"].lower()
            for i in range(len(self.patterns)):
                if self.patterns[i]["marker"] == 0:  # ещё не найден
                    if par.find(self.patterns[i]["text"]) >= 0:
                        self.patterns[i]["marker"] = 1
                        self.patterns[i]["paragraph_index"] = intro_par["number"]

        missing_components = []
        bold_missing = []

        for pattern in self.patterns:
            if not pattern["marker"]:
                missing_components.append(pattern["name"])
            elif self.check_bold and pattern["text"].lower() not in self.bold_check_exceptions:
                if not self._check_bold_formatting(pattern):
                    bold_missing.append(pattern["name"])

        errors = []
        if missing_components:
            missing_html = '<li>' + '</li><li>'.join(missing_components) + '</li>'
            errors.append(f'Не найдены следующие компоненты раздела "{self.chapter}": <ul>{missing_html}</ul>')

        if bold_missing:
            bold_html = '<li>' + '</li><li>'.join(bold_missing) + '</li>'
            errors.append(f'Следующие компоненты не выделены жирным шрифтом: <ul>{bold_html}</ul>')

        if errors:
            return answer(False, '<br>'.join(errors))
        else:
            suffix = ' и правильно отформатированы' if self.check_bold else ''
            return answer(True, f'Все необходимые компоненты раздела "{self.chapter}" обнаружены{suffix}!')
