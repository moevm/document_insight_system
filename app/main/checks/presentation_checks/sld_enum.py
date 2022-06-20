from utils import format_header
from ..base_check import BaseCheck, answer


class SldEnumCheck(BaseCheck):
    def __init__(self, file, pdf_id):
        super().__init__(file)
        self.pdf_id = pdf_id

    def check(self):
        error = []
        if self.file.slides[0].page_number[0] != -1:
            error.append(1)
        for i in range(1, len(self.file.slides)):
            if self.file.slides[i].page_number[0] != i + 1:
                error.append(i + 1)
        if not error:
            return answer(True, "Пройдена!")
        else:
            error = self.format_page_link(error)
            return answer(False, format_header('Не пройдена, проблемные слайды: {}'.format(', '.join(map(str, error)))), \
                          'Убедитесь в корректности формата номеров слайдов')
