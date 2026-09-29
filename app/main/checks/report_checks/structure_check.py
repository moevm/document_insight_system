from ..base_check import BaseReportCriterion, answer
from .style_check_settings import StyleCheckSettings


class ReportStructureCheck(BaseReportCriterion):
    label = "Проверка стуктуры отчета"
    _description = "Проверяет наличие обязательных заголовков и правильную последовательность разделов до ВВЕДЕНИЯ"
    id = "report_structure_check"

    def __init__(self, file_info, main_heading_style="heading 2", headers_map=None):
        super().__init__(file_info)
        self.required_sections = StyleCheckSettings.REQUIRED_SECTIONS_BEFORE_INTRO

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

    def check_needed_headers(self):
        if self.file.page_counter() < 4:
            return False, "В отчете недостаточно страниц. Нечего проверять."
        self.late_init()
        if not self.patterns:
            return False, (
                "Не удалось сформировать требуемые заголовки исходя из названия работы. Проверьте наименование работы."
            )
        result_string = ''
        patterns = []
        for pattern in self.patterns:
            patterns.append({"pattern": pattern, "marker": 0})
        if not len(self.headers):
            return False, "Не найдено ни одного заголовка.<br><br>Проверьте корректность использования стилей."
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
            result_str = 'Все необходимые заголовки обнаружены!'
            result_str += (
                f'<br><br><b>Ниже представлена иерархия обработанных заголовков, '
                f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            )
            result_str += self.chapters_str
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return True, result_str
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
            result_str += (
                f'<br><br><b>Ниже представлена иерархия обработанных заголовков, '
                f'сравните с Содержанием {self.format_page_link([self.headers_page])}:</b>'
            )
            result_str += self.chapters_str
            result_str += '<br>Если список не точный, убедитесь, что для каждого заголовка указан верный стиль.'
            return False, result_str

    def check_sequence_sections(self):
        paragraphs = self.file.paragraphs

        found_sections = []
        intro_found = False

        for paragraph in paragraphs:
            if not paragraph.paragraph_text:
                continue

            text = paragraph.paragraph_text.strip()
            style = str(paragraph.paragraph_style_name).lower()

            if "ВВЕДЕНИЕ" in text:
                if "heading 2" not in style:
                    return False, "Раздел 'ВВЕДЕНИЕ' должен быть оформлен стилем 'Заголовок 2'"
                intro_found = True
                break

            if "ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ" in text:
                if "heading 2" not in style:
                    return False, (
                        "Раздел 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ' должен быть оформлен стилем 'Заголовок 2'"
                    )
                found_sections.append("ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ")
                continue

            for section in self.required_sections:
                if section in text:
                    if "heading" in style:
                        f"Раздел '{section}' должен быть оформлен стилем 'Обычный', "
                        "а не как заголовок. Уберите стиль 'Заголовок' "
                        "и используйте обычный текст."
                    found_sections.append(section)
                    break

        if not intro_found:
            return False, "Не найден раздел 'ВВЕДЕНИЕ' (должен быть заголовком второго уровня)"

        if " ".join(found_sections) != " ".join(self.required_sections):
            result_str = (
                f"Ваша структура работы не соотвествует требуемой!"
                f"<br>Ваша структура: <br>   {'<br>'.join(found_sections)}"
                f"<br>Требуемая структура: <br>   {'<br>'.join(self.required_sections)}"
                f"Рекомендации:"
                f"<ul>"
                f"<li>Все разделы должны идти строго в указанном порядке</li>"
                f"<li>Разделы 'ЗАДАНИЕ', 'РЕФЕРАТ', 'ABSTRACT', 'СОДЕРЖАНИЕ' "
                "должны быть оформлены как обычный текст (стиль 'Обычный')</li>"
                f"<li>Раздел 'ОПРЕДЕЛЕНИЯ, ОБОЗНАЧЕНИЯ И СОКРАЩЕНИЯ' должен быть оформлен стилем 'Заголовок 2'</li>"
                f"</ul>"
            )
            return False, result_str

        return True, "Проверка последовательности разделов до раздела 'ВВЕДЕНИЕ' пройдена"

    def check(self):
        try:
            result_bool = True
            result_str = ""
            vkr_config = StyleCheckSettings.VKR_CONFIG['any_header']

            if vkr_config['check_presence']:
                result_bool_check_needed_headers, result_str_check_needed_headers = self.check_needed_headers()
                result_bool = result_bool and result_bool_check_needed_headers
                result_str += result_str_check_needed_headers

            if vkr_config['check_sequence']:
                result_bool_check_sequence_sections, result_str_check_sequence_sections = self.check_sequence_sections()
                result_bool = result_bool and result_bool_check_sequence_sections
                result_str += "<br>"
                result_str += "<br>"
                result_str += result_str_check_sequence_sections

            return answer(result_bool, result_str)

        except Exception as e:
            return answer(
                False,
                f"Ошибка при проверке стуктуры отчета: {str(e)}",
            )
