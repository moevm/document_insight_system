import re

from app.main.checks.base_check import BaseCheck, answer


class SearchKeyWord(BaseCheck):
    def __init__(self, presentation, key_slide, pdf_id):
        super().__init__(presentation)
        self.key_slide = f"({'|'.join((key.lower() for key in key_slide))})"
        self.pdf_id = pdf_id

    def check(self):
        for i, text in enumerate(self.presentation.get_text_from_slides(), 1):
            if re.search(self.key_slide, str(text).lower()):
                found = self.format_page_link([i])
                return answer(True, 'Найден под номером: {}'.format(', '.join(map(str, found))))
        return answer(False, 'Слайд не найден')
