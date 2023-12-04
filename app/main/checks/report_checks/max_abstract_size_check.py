from ..base_check import BaseReportCriterion, answer


class ReportMaxSizeOfAbstractCheck(BaseReportCriterion):
    description = "Максимальный размер раздела Реферат в ВКР"
    id = "max_abstract_size_check"

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.referat_size = 0
        self.abstract_size = 0
        self.max_size = 0

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])
        self.max_size = 1
        referat_page = 0
        abstract_page = 0
        main_page = 0
        for header in self.headers:
            if header["name"] == "Реферат":
                referat_page = header["page"]
            if header["name"] == "Abstract":
                abstract_page = header["page"]
            if header["name"] == "Содержание":
                main_page = header["page"]
        self.referat_size = abstract_page - referat_page
        self.abstract_size = main_page - abstract_page

    def check(self):
        self.late_init()
        if self.referat_size > self.max_size and self.abstract_size > self.max_size:
            return answer(False,
                          f"<br><br>Размеры разделов \"Реферат\" и \"Abstract\" превышает максимальный размер")
        if self.referat_size > self.max_size:
            return answer(False,
                          f"<br><br>Размер раздела \"Реферат\" равен {self.referat_size} страницы, должен быть {self.max_size}")
        if self.abstract_size > self.max_size:
            return answer(False,
                          f"<br><br>Размер раздела \"Abstract\" равен {self.abstract_size} страницы, должен быть {self.max_size}")
        return answer(True,
                      f"<br><br>Размеры разделов \"Реферат\" и \"Abstract\" соответствуют шаблону")
