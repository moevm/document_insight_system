from ..base_check import BaseReportCriterion, answer


class ReportFirstPagesCheck(BaseReportCriterion):
    description = "Проверка наличия обязательных страниц в отчете"
    id = 'first_pages_check'
    priority = True

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        self.late_init()
        result_str = ''
        for header in self.headers:
            if not header["marker"]:
                result_str += '<li>' + header["name"] + '</li>'

        if not result_str:
            return answer(True,
                          "Все обязательные страницы найдены и их заголовки находятся на первой строке новой страницы.")
        else:
            return answer(False,
                          f'Следующие страницы не найдены либо их заголовки расположены не на первой строке новой '
                          f'страницы: <ul>{result_str}</ul> Проверьте очередность листов и орфографию заголовков.')
