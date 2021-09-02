from app.main.checks.base_check import BaseCheck, answer
import re


class SldEnumCheck(BaseCheck):
    def __init__(self, presentation):
        super().__init__(presentation)

    def check(self):
        error = []
        if self.presentation.slides[0].page_number[0] != -1:
            error.append(1)
        for i in range(1, len(self.presentation.slides)):
            if self.presentation.slides[i].page_number[0] != i + 1:
                error.append(i+1)
        if not error:
            return answer(True, error, "Пройдена!")
        else:
            return answer(False, error, 'Не пройдена, проблемные слайды: {}'.format(', '.join(map(str, error))), \
                                        'Убедитесь в корректности формата номеров слайдов')
