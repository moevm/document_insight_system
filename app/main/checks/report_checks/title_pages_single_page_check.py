from ..base_check import BaseReportCriterion, answer


class TitlePagesSinglePage(BaseReportCriterion):
    label = "Проверка, что титульные страницы занимают не более одной страницы"
    id = "title_pages_single_page"

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []
        self.pages = {}

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])
        self.pages = self.file.pdf_file.get_text_on_page()

    def _get_first_line(self, page_num):
        text = self.pages.get(page_num, "")
        return text.split("\n")[0].lower().strip()

    def _next_page_has_header_key(self, page_num, header_index):
        first_line = self._get_first_line(page_num + 1)
        for header in self.headers[header_index + 1:]:
            if header["key"] in first_line:
                return True
        return False

    def check(self):
        self.late_init()

        violations = []
        for i, header in enumerate(self.headers):
            if not header["marker"]:
                continue
            if i == len(self.headers) - 1:
                continue
            if not self._next_page_has_header_key(header["page"], i):
                page_links = self.format_page_link([header["page"], header["page"] + 1])
                pages_str = ', '.join(page_links)
                violations.append(f'"{header["name"]}" занимает более одной страницы (стр. {pages_str})')

        if not violations:
            return answer(True, "Каждая титульная страница занимает не более одного листа.")
        return answer(False, '<br>'.join(violations))
