from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer


class ReportNeededHeadersCheck(BaseReportCriterion):
    description = "Проверка наличия обязательных заголовков в отчете"
    id = 'needed_headers_check'
    priority = True

    def __init__(self, file_info, main_heading_style="heading 2"):
        super().__init__(file_info)
        self.headers_page = 1
        self.headers = []
        self.main_heading_style = main_heading_style
        self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]

    def late_init(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.headers_page = self.file.find_header_page(self.file_type['report_type'])

    def show_chapters(self):
        chapters_str = "<br>"
        for header in self.headers:
            if header["style"] == self.main_heading_style:
                chapters_str += header["text"] + "<br>"
            else:
                chapters_str += "&nbsp;&nbsp;&nbsp;&nbsp;" + header["text"] + "<br>"
        return chapters_str

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
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
            result_str += f'<br><br><b>&nbsp;&nbsp;&nbsp;&nbsp;Ниже представлена иерархия обработанных заголовков, ' \
                          f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            result_str += self.show_chapters()
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
            result_str += f'<br><br><b>&nbsp;&nbsp;&nbsp;&nbsp;Ниже представлена иерархия обработанных заголовков, ' \
                          f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            result_str += self.show_chapters()
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return answer(False, result_str)
