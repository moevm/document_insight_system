from ..base_check import BaseReportCriterion, answer


class ReportHeadersAtPageTopCheck(BaseReportCriterion):
    description = "Проверка расположения разделов первого уровня с новой страницы"
    id = "headers_at_page_top_check"

    def __init__(self, file_info, headers=[]):
        super().__init__(file_info)
        self.headers_page = 1
        self.chapters = []
        self.headers = headers
        self.pdf = self.file.pdf_file if self.file else None

    def late_init_vkr(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])
        self.headers = self.find_headers()
        self.headers_page = self.file.find_header_page(self.file_type['report_type'])

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = True
        result_str = ""
        if self.file_type["report_type"] == 'LR':
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
        elif self.file_type["report_type"] == 'VKR':
            self.late_init_vkr()
            for page_num in range(1, self.file.page_counter() + 1):
                if not self.headers:
                    return answer(False,
                                  "Не найдено ни одного заголовка второго уровня.<br><br>"
                                  "Проверьте корректность использования стилей.")
                collected_text = self.file.first_lines[page_num - 1]
                for header in self.headers:
                    if not header["marker"]:
                        header_text = header["text"].lower()
                        if collected_text.startswith(header_text.strip()):
                            header["marker"] = 1
                            break
                        elif collected_text.find(header_text.strip()) > 0:
                            result_str += (("<br>" if len(result_str) else "") +
                                           f"Заголовок второго уровня \"{header['text']}\" "
                                           f"находится не в начале страницы или пронумирован с помощью списка "
                                           f"{self.format_page_link([page_num])}. ")
                            header["marker"] = 1
                            break

            for header in self.headers:
                if not header["marker"]:
                    result = False
                    result_str += (("<br>" if len(result_str) else "") +
                                   f"Заголовок второго уровня \"{header['text']}\" "
                                   f"находится не в начале страницы или занимает больше двух строк.")
        else:
            result_str = "Во время обработки произошла критическая ошибка"
            return answer(False, result_str)

        if not result_str:
            result_str = "Все требуемые разделы начинаются с новой страницы."
        else:
            result_str += f"<br><br>Если сгенерированный PDF-файл {self.format_page_link([self.headers_page])} " \
                          f"имеет проблемы с оформлением, попробуйте загрузить свой PDF."
        return answer(result, result_str)

    def find_headers(self):
        chapters = []
        for header in self.chapters:
            if header["style"] == 'heading 2':
                if header["text"].find("ПРИЛОЖЕНИЕ") >= 0:
                    break
                chapters.append({"text": header["text"], "marker": 0})
        return chapters
