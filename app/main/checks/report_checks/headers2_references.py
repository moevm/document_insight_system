from ..base_check import BaseReportCriterion, answer


class ReportHeaders2ReferencesCheck(BaseReportCriterion):
    label = "Проверка отсутствия ссылок в заголовках второго уровня"
    _description = ''
    id = "headers2_references_check"

    def __init__(self, file_info, headers=[]):
        super().__init__(file_info)
        self.headers_page = 1
        self.chapters = []
        self.headers = headers
        self.pdf = self.file.pdf_file if self.file else None

    def late_init_vkr(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])
        self.headers = self.find_headers()

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        result = True
        result_str = ""

        if self.file_type["report_type"] == 'LR':
            pass

        elif self.file_type["report_type"] == 'VKR':
            self.late_init_vkr()
            for header in self.headers:
                header_text = header["text"].lower()
                if contain_references(header_text):
                    break
                elif !contain_references(header_text):
                    result_str += (("<br>" if len(result_str) else "") +
                                   f"Заголовок второго уровня \"{header['text']}\" "
                                   f"содержит ссылки. ")
                    break

        else:
            result_str = "Во время обработки произошла критическая ошибка - указан неверный тип работы в наборе критериев"
            return answer(False, result_str)

        if not result_str:
            result_str = "В заголовках второго уровня нет ссылок"
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
                chapters.append({"text": header["text"]})
        return chapters

    def contain_references(self, header_text):
        if '[' in header_text and ']' in header_text:
            return True
        return False
