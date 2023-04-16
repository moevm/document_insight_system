from ..base_check import BaseReportCriterion, answer


class ReportMainCharacterCheck(BaseReportCriterion):
    description = "Проверка фамилии заведующего кафедрой"
    id = 'main_character_check'

    def __init__(self, file_info, main_character_name_right="Лисс", main_character_name_wrong="Кринкин"):
        super().__init__(file_info)
        self.headers = []
        self.main_character_name_right = main_character_name_right
        self.main_character_name_wrong = main_character_name_wrong

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])


    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        self.late_init()
        result_str = ''
        for header in self.headers:
            if header["marker"] and header["main_character"]:
                page = header["page"]
                text_on_page = self.file.pdf_file.text_on_page[page]
                if text_on_page.find(self.main_character_name_wrong) >= 0 and not text_on_page.find(self.main_character_name_right) >= 0:
                    result_str += f"На странице {self.format_page_link([page])} указана неверная фамилия заведующего кафедрой. Убедитесь, что И.О. зав. кафедрой А.А. Лисс.<br>"
                elif not text_on_page.find(self.main_character_name_right) >= 0:
                    result_str += f"На странице {self.format_page_link([page])} нет И.О. заведующего кафедрой, в графе зав. кафедрой должно быть указано А.А. Лисс.<br>"
        if not result_str:
            return answer(True, 'ФИО заведующего кафедрой указано верно на всех листах.')
        else:
            return answer(False, result_str)
