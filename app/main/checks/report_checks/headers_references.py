from ..base_check import BaseReportCriterion, answer


class ReportHeadersReferencesCheck(BaseReportCriterion):
    label = "Проверка отсутствия ссылок в заголовках"
    _description = ''
    id = "headers_references_check"

    REFERENCE_PATTERN = r'\[[\^]{0,1}[\d \-,]+\]'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.chapters = []

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])
        self.headers = self.find_headers()

    def check(self):
        self.late_init()

        if not self.headers:
            return answer(False, "В отчёте не было найдено заголовков.")

        result = True
        result_str = ""

        for header in self.headers:
            if self.contain_references(header['text']):
                page_info = f" (стр. {header['page']})" if header['page'] != -1 else ""
                result_str += (
                    "<br>" if len(result_str) else ""
                ) + f"Заголовок \"{header['text']}\"{page_info} содержит ссылки."

        if not result_str:
            result_str = "В заголовках нет ссылок"
        else:
            result = False
            result_str += (
                f"<br><br>Если сгенерированный PDF-файл {self.format_page_link([self.headers_page])} "
                f"имеет проблемы с оформлением, попробуйте загрузить свой PDF."
            )

        return answer(result, result_str)

    def find_headers(self):
        '''находим заголовки и добавляем страницы для тех, у которых они явно указаны'''
        headers = []

        for header in self.chapters:
            headers.append({'text': header['text'], 'page': -1})  # страницы нет = -1

        main_headers = self.file.make_headers(self.file_type['report_type'])
        for main_header in main_headers:
            for header in headers:
                if main_header['name'] == header['text']:
                    header['page'] = main_header['page']

        return headers

    def contain_references(self, header_text):
        return bool(re.search(self.REFERENCE_PATTERN, header_text))
