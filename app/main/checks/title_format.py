from app.main.checks.base_check import BaseCheck, answer
import re
import itertools

class TitleFormatCheck(BaseCheck):
    def __init__(self, presentation, pdf_id):
        super().__init__(presentation)
        self.empty_headers = []
        self.len_exceeded = []
        self.pdf_id = pdf_id

    def exceeded_verdict(self):
        return 'Превышение длины: {}'.format(', '.join(map(str,  self.format_page_link(self.len_exceeded)))), \
               'Убедитесь в корректности заголовка и текста слайда'

    def empty_verdict(self):
        return 'Заголовки не найдены: {}.'.format(', '.join(map(str,  self.format_page_link(self.empty_headers)))), \
               'Убедитесь, что слайд озаглавлен соответстующим элементом'

    def get_failing_headers(self):
        for i, title in enumerate(self.presentation.get_titles(), 1):
            if title == "":
                self.empty_headers.append(i)
                continue

            title = str(title).replace('\x0b', '\n')
            if '\n' in title or '\r' in title:
                titles = [t for t in re.split('\r|\n', title) if t != '']
                if len(titles) > 2:
                    self.len_exceeded.append(i)

        return self.empty_headers, self.len_exceeded

    def check(self):
        self.get_failing_headers()
        error_slides = list(itertools.chain(self.empty_headers, self.len_exceeded))
        if not error_slides:
            return answer(not bool(error_slides), [self.empty_headers, self.len_exceeded], "Пройдена!")
        elif len(self.empty_headers) == 0 and len(self.len_exceeded) != 0:
            return answer(False, self.len_exceeded, *self.exceeded_verdict())
        elif len(self.empty_headers) != 0 and len(self.len_exceeded) == 0:
            return answer(False, self.empty_headers, *self.empty_verdict())
        else:
            return answer(False, [self.empty_headers, self.len_exceeded],
                   *list(itertools.chain(self.empty_verdict(), self.exceeded_verdict())))
