from ..base_check import BaseReportCriterion, answer


class ReportNeededPages(BaseReportCriterion):
    description = "Проверка наличия обязательных страниц в отчете"
    id = 'first_pages_check'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        result_str = ''
        for header in self.headers:
            if not header["marker"]:
                result_str += '<li>' + header["name"]  + '</li>'

        result_score = 0
        if result_str == '':
            result_score = 1
        if result_score:
            return answer(result_score, "Все обязательные страницы найдены и их заголовки находятся на первой строке новой страницы.")
        else:
            return answer(result_score,
                          f'Следующие страницы не найдены либо их заголовки расположены не на первой строке новой страницы: <ul>{result_str}</ul>' +
                          'Проверьте очередность листов и орфографию заголовков.')
