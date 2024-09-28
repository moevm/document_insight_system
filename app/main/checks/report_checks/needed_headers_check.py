
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
                self.headers_main = 'any_header'
                self.patterns = StyleCheckSettings.CONFIGS.get(self.config)['any_header']['headers']
                self.second_lvl_headers = StyleCheckSettings.CONFIGS.get(self.config).get('second_header', {}).get('second_header_check')

    def find_headers_second_lvl(self, header_ind, header_text):
        result_string_second_lvl = ''
        final_str = ''
        start_ind = header_ind+1
        patterns_for_sec_lvl = []
        for pattern in self.second_lvl_headers[header_text]:
            patterns_for_sec_lvl.append({"pattern": pattern, "marker": 0})
        for header in self.headers[start_ind:]:
            if header['style'] in StyleCheckSettings.CONFIGS.get(self.config)['second_header']["docx_style"]:
                for i in range(len(patterns_for_sec_lvl)):
                    pattern = patterns_for_sec_lvl[i]["pattern"]
                    if header['text'].lower().find(pattern) >= 0:
                        patterns_for_sec_lvl[i]["marker"] = 1
            if header['style'] in StyleCheckSettings.CONFIGS.get(self.config)[self.headers_main]["docx_style"]:
                break

        for pattern in patterns_for_sec_lvl:
            if not pattern["marker"]:
                result_string_second_lvl += '<li>' + pattern["pattern"].upper() + '</li>'
            if result_string_second_lvl:
                final_str = f'Подразделы главы "{header_text.upper()}":' + f'<ul>{result_string_second_lvl}</ul>'
        return final_str

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        if not self.patterns:
            return answer(False, "Не удалось сформировать требуемые заголовки исходя из названия работы. Проверьте наименование работы.")
        result_string = ''
        result_string_second_lvl = ''
        patterns = []
        for pattern in self.patterns:
            patterns.append({"pattern": pattern, "marker": 0})
        if not len(self.headers):
            return answer(False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей.")
        header_ind = -1
        for header in self.headers:
            header_text = header["text"].lower()
            header_ind += 1
            if self.second_lvl_headers:
                if header_text in self.second_lvl_headers:
                    result_string_second_lvl = self.find_headers_second_lvl(header_ind, header_text)
            for i in range(len(patterns)):
                pattern = patterns[i]["pattern"]
                if header_text.find(pattern) >= 0:
                    patterns[i]["marker"] = 1

        for pattern in patterns:
            if not pattern["marker"]:
                result_string += '<li>' + pattern["pattern"].upper() + '</li>'

        if not result_string:
            result_str = f'Все необходимые заголовки обнаружены!'
            result_str += f'<br><br><b>Ниже представлена иерархия обработанных заголовков, ' \
            f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            result_str += self.chapters_str
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return answer(True, result_str)
        else:
            result_str = f'Не найдены следующие обязательные заголовки: <ul>{result_string}</ul>'
            result_str += result_string_second_lvl
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
