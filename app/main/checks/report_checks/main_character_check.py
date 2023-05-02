from ..base_check import BaseReportCriterion, answer


class ReportMainCharacterCheck(BaseReportCriterion):
    description = "Проверка фамилии и должности заведующего кафедрой"
    id = 'main_character_check'
    priority = True

    def __init__(self, file_info, main_character_name_right="А.А. Лисс", main_character_name_wrong="К.В. Кринкин",
                 main_character_job_right="И.о. зав. кафедрой", main_character_job_wrong="Зав. кафедрой"):
        super().__init__(file_info)
        self.headers = []
        self.main_character_name_right = main_character_name_right
        self.main_character_name_wrong = main_character_name_wrong
        self.main_character_job_right = main_character_job_right
        self.main_character_job_wrong = main_character_job_wrong

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
                if text_on_page.find(self.main_character_name_wrong) >= 0 and not text_on_page.find(
                        self.main_character_name_right) >= 0:
                    result_str += f"На странице {self.format_page_link([page])} указана неверная фамилия заведующего " \
                                  f"кафедрой. Убедитесь, что И.о. зав. кафедрой {self.main_character_name_right}.<br>"
                elif not text_on_page.find(self.main_character_name_right) >= 0:
                    result_str += f"На странице {self.format_page_link([page])} не указано ФИО заведующего кафедрой, в " \
                                  f"графе И.о. зав. кафедрой должно быть указано {self.main_character_name_right}.<br>"
                if text_on_page.find(self.main_character_job_wrong) >= 0 and not text_on_page.find(
                        self.main_character_job_right) >= 0:
                    result_str += f'На странице {self.format_page_link([page])} указана неверная должность ' \
                                  f'заведующего кафедрой, должно быть "{self.main_character_job_right}".<br>'
        if not result_str:
            return answer(True, 'ФИО и должность исполняющего обязанности зав. кафедрой указаны верно на всех листах.')
        else:
            result_str += f'<br>Убедитесь, что вы использовали правильные формы бланков титульного листа, задания и календарного плана.' \
                          f'<br>Для бакалавров: <a href="https://drive.google.com/drive/folders/1pvv9HJIUB0VZUXteGqtLcVq6zIgZ6rbZ">Формы бланков для бакалавров</a>.' \
                          f'<br>Для магистров: <a href="https://drive.google.com/drive/folders/1KOoXzKv4Wf-XyGzOf1X8gN256sgame1D">Формы бланков для магистров</a>.'
            return answer(False, result_str)
