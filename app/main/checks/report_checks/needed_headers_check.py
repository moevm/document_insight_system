from .style_check_settings import StyleCheckSettings
from ..base_check import BaseReportCriterion, answer


class ReportNeededHeadersCheck(BaseReportCriterion):
    label = "Проверка наличия обязательных заголовков в отчете"
    description = ''
    id = 'needed_headers_check'
    priority = True

<<<<<<< HEAD
    def __init__(self, file_info, main_heading_style="heading 2", headers_map = None):
=======
    def __init__(self, file_info, main_heading_style="heading 2", headers_map=None):
>>>>>>> master
        super().__init__(file_info)
        self.headers_page = 1
        self.headers = []
        self.main_heading_style = main_heading_style
<<<<<<< HEAD
        if headers_map:
            self.config = headers_map
        else:    
            self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
        self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]
        self.patterns_second_lvl = StyleCheckSettings.CONFIGS.get(self.config)[1]["headers"]
=======
        self.patterns = []
        if headers_map:
            self.config = headers_map
        else:
            self.config = 'VKR_HEADERS' if (self.file_type['report_type'] == 'VKR') else 'LR_HEADERS'
            self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]
>>>>>>> master

    def late_init(self):
        self.headers = self.file.make_chapters(self.file_type['report_type'])
        self.headers_page = self.file.find_header_page(self.file_type['report_type'])
<<<<<<< HEAD

    def show_chapters(self):
        chapters_str = "<br>"
        for header in self.headers:
            if header["style"] == self.main_heading_style:
                chapters_str += header["text"] + "<br>"
            else:
                chapters_str += "&nbsp;&nbsp;&nbsp;&nbsp;" + header["text"] + "<br>"
        return chapters_str
    
    def find_headers_second_lvl(self, header_ind, header_text):
        result_string_second_lvl = ''
        final_str = ''
        start_ind = header_ind+1
        patterns_for_sec_lvl = []
        for pattern in self.patterns_second_lvl:
            patterns_for_sec_lvl.append({"pattern": pattern, "marker": 0})
        for header in self.headers[start_ind:]:
            if header['style'] in StyleCheckSettings.CONFIGS.get(self.config)[1]["docx_style"]:
                for i in range(len(patterns_for_sec_lvl)):
                    pattern = patterns_for_sec_lvl[i]["pattern"]
                    if header['text'].lower().find(pattern.lower()) >= 0:
                        patterns_for_sec_lvl[i]["marker"] = 1
            if header['style'] in StyleCheckSettings.CONFIGS.get(self.config)[0]["docx_style"]:
                break              

        for pattern in patterns_for_sec_lvl:
            if not pattern["marker"]:
                result_string_second_lvl += '<li>' + pattern["pattern"] + '</li>'
            if result_string_second_lvl:
                final_str = f'подразделы главы "{header_text.upper()}": ' + result_string_second_lvl
        return final_str    
=======
        self.chapters_str = self.file.show_chapters(self.file_type['report_type'])
        # TODO: change
        self.headers_main = self.file.get_main_headers(self.file_type['report_type'])
        if self.headers_main == "Задание 1":
            self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[0]["headers"]
        elif self.headers_main == "Задание 2":
            self.patterns = StyleCheckSettings.CONFIGS.get(self.config)[1]["headers"]
>>>>>>> master

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
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
            if header_text == 'результаты работы в весеннем семестре' and self.patterns_second_lvl:
                result_string_second_lvl = self.find_headers_second_lvl(header_ind, header_text)

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
<<<<<<< HEAD
            result_str = f'Не найдены следующие обязательные заголовки: <ul>{result_string}\n{result_string_second_lvl}</ul>'
            result_str += f'Если не найден существующий раздел, попробуйте сделать следующее:<ul>' \
                            f'<li>Убедитесь в отсутствии опечаток и лишних пробельных символов в названии раздела;</li>' \
                            f'<li>Убедитесь в соответствии стиля заголовка требованиям к отчету по ВКР;</li>'\
                            f'<li>Убедитесь, что заголовок состоит из одного абзаца.</li></ul>'

            result_str += f'<br><br><b>&nbsp;&nbsp;&nbsp;&nbsp;Ниже представлена иерархия обработанных заголовков, ' \
=======
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
>>>>>>> master
                          f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            result_str += self.chapters_str
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return answer(False, result_str)
