from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer


class ReportNeededHeadersCheck(BaseReportCriterion):
    label = "Проверка наличия обязательных заголовков в отчете"
    description = ''
    id = 'needed_headers_check'
    priority = True

    def __init__(self, file_info, main_heading_style="heading 2", headers_map=None):
        super().__init__(file_info)
        self.headers_page = 1
        self.headers = []
        self.main_heading_style = main_heading_style
        self.patterns = []
        if headers_map:
            self.config = headers_map
        else:
            self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
            # self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]

    def late_init(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.headers_page = self.file.find_header_page(self.file_type['report_type'])
        self.chapters_str = self.file.show_chapters(self.file_type['report_type'])
        self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
        if self.headers_main in StyleCheckSettings.CONFIGS.get(self.config):
            self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]['headers']
        else:
            if 'any_header' in StyleCheckSettings.CONFIGS.get(self.config):
                self.patterns = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['headers']

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        if not self.patterns:
            return answer(False, "Не удалось сформировать требуемые заголовки исходя из названия работы. Проверьте наименование работы.")
        result_string = ''
        patterns = []
        for pattern in self.patterns:
            patterns.append({"pattern": pattern, "marker": 0})
        if not len(self.headers):
            return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
        for header in self.headers:
            header_text = header["text"].lower()
            for i in range(len(patterns)):
                pattern = patterns[i]["pattern"]
                if header_text.find(pattern.lower()) >= 0:
                    patterns[i]["marker"] = 1

        for pattern in patterns:
            if not pattern["marker"]:
                result_string += '<li>' + pattern["pattern"] + '</li>'

        if not result_string:
            result_str = f'Все необходимые заголовки обнаружены!'
            result_str += f'<br><br><b>Ниже представлена иерархия обработанных заголовков, ' \
                        f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            result_str += self.chapters_str
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return answer(True, result_str)
        else:
            result_str = f'Не найдены следующие обязательные заголовки: <ul>{result_string}</ul>'
            result_str += '''
                        Если не найден существующий раздел, попробуйте сделать следующее:
                        <ul>
                            <li>Убедитесь в отсутствии опечаток и лишних пробельных символов в названии раздела;</li>
                            <li>Убедитесь в соответствии стиля заголовка требованиям к отчету по ВКР;</li>
                            <li>Убедитесь, что заголовок состоит из одного абзаца.</li>
                        </ul>
                        '''
            result_str += f'<br><br><b>Ниже представлена иерархия обработанных заголовков, ' \
                        f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            result_str += self.chapters_str
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return answer(False, result_str)
