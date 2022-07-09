from ..base_check import BaseReportCriterion, answer


class ReportHeadersAtPageTopCheck(BaseReportCriterion):
    description = "Проверка расположения разделов первого уровня с новой страницы"
    id = "headers_at_page_top_check"

    def __init__(self, file_info, headers):
        super().__init__(file_info)
        self.headers = headers
        self.pdf = self.file.pdf_file

    def check(self):
        result = True
        result_str = ""
        for header in self.headers:
            found = False
            for page_num in range(1, self.pdf.page_count):
                lines = self.pdf.text_on_page[page_num + 1].split("\n")
                last_header_line = 0
                collected_text = ""
                while True:
                    collected_text += " "
                    collected_text += lines[last_header_line]
                    collected_text = collected_text.strip()
                    if collected_text.lower() == header.lower():
                        found = True
                        break
                    # first condition is needed for cases like that: collected_text == [""]
                    if len(collected_text) > 0 and header.lower().startswith(collected_text.lower()):
                        last_header_line += 1
                    else:
                        break
                if found:
                    break
            if not found:
                result = False
                result_str += (("<br>" if len(result_str) else "")
                               + f"Заголовка \"{header}\" нет в документе или он находится не в начале страницы.")
        if len(result_str) == 0:
            result_str = "Все требуемые разделы начинаются с новой страницы."
        return answer(result, result_str)
