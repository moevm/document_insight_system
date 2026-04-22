from ..base_check import BaseReportCriterion, answer


class ReportGapsBetweenTitleAndTextCheck(BaseReportCriterion):
    label = "Не должно быть висячих заголовков (когда заголовок и абзац текста расположены на разных страницах)"
    id = "report_gaps_between_title_and_text_check"

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        try:
            headers = self.file.make_chapters(self.file_type["report_type"])
            if not headers:
                return answer(False, "Не найдено ни одного заголовка.")

            headers_info = []
            for header in headers:
                if "heading" in header.get("style"):
                    header_name = header.get("text")
                    header_text = header.get("child")[0].get("text")[:40]
                    headers_info.append(
                        {
                            "header": header_name,
                            "header_text": header_text,
                            "page_num": None,
                            "header_is_found": False,
                        }
                    )

            page_counter = self.file.page_counter()
            fail_headers_info = []
            current_header_idx = 0

            for page_num in range(1, page_counter + 1):
                text_on_page = self.file.pdf_file.text_on_page[page_num]

                while current_header_idx < len(headers_info):
                    header_info = headers_info[current_header_idx]

                    if header_info.get("header_is_found") == True:
                        current_header_idx += 1
                        continue

                    header_is_found = header_info["header"] in text_on_page
                    text_is_found = header_info["header_text"] in text_on_page

                    if header_is_found:
                        if not text_is_found:
                            header_info["page_num"] = page_num
                            header_info["header_is_found"] = True
                            fail_headers_info.append(header_info)
                        current_header_idx += 1
                    else:
                        break

            if len(fail_headers_info) == 0:
                return answer(
                    True,
                    "Проверка разрывов между заголовком и текстом пройдена! Все заголовки и следующий за ними текст находятся на одной странице.",
                )

            pages_str = "<br>   ".join(
                f"{info['header']} (стр. {info['page_num']})<br>"
                for info in fail_headers_info
            )

            return answer(
                False,
                f"Проверка разрывов между заголовком и текстом не пройдена!<br>"
                f"Обнаружены висячие заголовки:<br> {pages_str}<br><br>"
                f"Как исправить:<br>"
                f"1. Найдите заголовки на указанных страницах<br>"
                f"2. Убедитесь, что после заголовка есть хотя бы 1 строка текста<br>"
                f"3. Если заголовок внизу страницы, добавьте разрыв страницы перед ним<br>",
            )

        except Exception as e:
            return answer(
                False,
                f"Ошибка при проверке разрывов между заголовком и текстом: {str(e)}",
            )
