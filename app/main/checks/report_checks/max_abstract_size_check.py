from ..base_check import BaseReportCriterion, answer


class ReportMaxSizeOfAbstractCheck(BaseReportCriterion):
    label = "Максимальный размер раздела Реферат в ВКР"
    _description = "Максимальный размер раздела Реферат в ВКР (1 стр.)"
    id = "max_abstract_size_check"

    def __init__(
        self, file_info, max_size=1, referat_header='Реферат', abstract_header='Abstract', contents_header='Содержание'
    ):
        super().__init__(file_info)
        self.headers = []
        self.referat_size = 0
        self.abstract_size = 0
        self.max_size = max_size
        self.section_names = (referat_header, abstract_header, contents_header)

    def late_init(self):
        if self.section_names == ('Реферат', 'Abstract', 'Содержание'):
            self.headers = self.file.make_headers(self.file_type['report_type'])
        else:
            self.headers = self.file.make_headers(self.file_type['report_type'], self.section_names)
        referat_page = 0
        abstract_page = 0
        main_page = 0
        for header in self.headers:
            if header["name"] == self.section_names[0]:
                referat_page = header["page"]
            if header["name"] == self.section_names[1]:
                abstract_page = header["page"]
            if header['name'].replace('C', 'С') == self.section_names[2]:
                main_page = header["page"]
        self.valid_pages = 0 < referat_page < abstract_page < main_page
        self.referat_size = abstract_page - referat_page
        self.abstract_size = main_page - abstract_page

    def check(self):
        if not hasattr(self.file, 'make_headers'):
            return answer(False, 'Проверка реферата применима к отчётам DOCX.')
        self.late_init()
        if not self.valid_pages:
            return answer(False, 'Не найдены разделы реферата, Abstract и содержания в требуемом порядке.')
        if self.referat_size > self.max_size and self.abstract_size > self.max_size:
            return answer(False, "<br><br>Размеры разделов \"Реферат\" и \"Abstract\" превышает максимальный размер")
        if self.referat_size > self.max_size:
            return answer(
                False,
                f"<br><br>Размер раздела \"Реферат\" равен {self.referat_size} страницы, должен быть {self.max_size}",
            )
        if self.abstract_size > self.max_size:
            return answer(
                False,
                f"<br><br>Размер раздела \"Abstract\" равен {self.abstract_size} страницы, должен быть {self.max_size}",
            )
        return answer(True, "<br><br>Размеры разделов \"Реферат\" и \"Abstract\" соответствуют шаблону")
