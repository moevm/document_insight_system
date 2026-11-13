from ..base_check import BaseReportCriterion, answer


class ReportFirstPagesCheck(BaseReportCriterion):
    label = "Проверка наличия обязательных страниц в отчете"
    _description = (
        'Обязательные страницы: Титульный лист, Задание на выпускную квалификационную работу, '
        'Календарный план, Реферат, Abstract, Cодержание'
    )
    id = 'first_pages_check'
    priority = True

    def __init__(self, file_info, headers=None):
        super().__init__(file_info)
        self.headers = []
        self.required_headers = headers

    def late_init(self):
        self.headers = (
            self.file.make_headers(self.file_type['report_type'], self.required_headers)
            if self.required_headers is not None
            else self.file.make_headers(self.file_type['report_type'])
        )

    def check(self):
        if not hasattr(self.file, 'make_headers'):
            return answer(False, 'Проверка первых страниц применима к отчётам DOCX.')
        self.late_init()
        if not self.headers:
            return answer(False, 'Не задан список обязательных первых страниц для этого типа отчёта.')
        result_str = ''
        for header in self.headers:
            if not header["marker"]:
                result_str += '<li>' + header["name"] + '</li>'

        if not result_str:
            return answer(
                True, "Все обязательные страницы найдены и их заголовки находятся на первой строке новой страницы."
            )
        else:
            return answer(
                False,
                f'Следующие страницы не найдены либо их заголовки расположены не на первой строке новой '
                f'страницы: <ul>{result_str}</ul> Проверьте очередность листов и орфографию заголовков.',
            )
