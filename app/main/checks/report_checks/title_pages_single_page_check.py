from ..base_check import BaseReportCriterion, answer


class TitlePagesSinglePage(BaseReportCriterion):
    label = "Проверка, что титульные страницы занимают не более одной страницы"
    id = "title_pages_single_page"

    def __init__(self, file_info):
        super().__init__(file_info)
        self.headers = []

    def late_init(self):
        self.headers = self.file.make_headers(self.file_type['report_type'])

    def check(self):
        self.late_init()

        found = [header for header in self.headers if header["marker"]]
        violations = []
        for current, following in zip(found, found[1:], strict=False):
            last_page = following["page"] - 1
            if last_page > current["page"]:
                pages_str = '–'.join(self.format_page_link([current["page"], last_page]))
                violations.append(f'"{current["name"]}" занимает более одной страницы (стр. {pages_str})')

        if not violations:
            return answer(True, "Каждая титульная страница занимает не более одного листа.")
        return answer(False, '<br>'.join(violations))
