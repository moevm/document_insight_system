from ..base_check import BaseReportCriterion, answer

class ReportHeadersReferencesCheck(BaseReportCriterion):
    label = "Проверка отсутствия ссылок в заголовках"
    _description = ''
    id = "headers_references_check"

    def __init__(self, file_info):
        super().__init__(file_info)
        self.chapters = self.file.make_chapters(self.file_type['report_type'])
        self.headers = self.find_headers()
        self.optional_headers == False

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        if self.file_type['report_type'] == 'LR':
            self.optional_headers == True
        elif self.file_type['report_type'] != 'VKR':
            return answer(False, "Во время обработки произошла критическая ошибка - указан неверный тип работы в наборе критериев")

        if not self.headers:
            answer_str = "В отчёте не было найдено заголовков."
            return answer(self.optional_headers, answer_str)

        result = True
        result_str = ""

        for header in self.headers():
            header_text = header["text"].lower()
            if self.contain_references(header_text):
                #добавить номер страницы
                result_str += (("<br>" if len(result_str) else "") +
                                   f"Заголовок\"{header['text']}\" "
                                   f"содержит ссылки. ")

        if not result_str:
            result_str = "В заголовках нет ссылок"
        else:
            result = False
            result_str += f"<br><br>Если сгенерированный PDF-файл {self.format_page_link([self.headers_page])} " \
                          f"имеет проблемы с оформлением, попробуйте загрузить свой PDF."

        return answer(result, result_str)


    def find_headers(self):
        headers = []
        for header in self.chapters:
            #добавить поиск страницы
            headers.append({"text": header["text"]})
        return headers

    def contain_references(self, header_text):
        if '[' in header_text and ']' in header_text:
            return True
        return False
