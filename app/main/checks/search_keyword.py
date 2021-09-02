from app.main.checks.base_check import BaseCheck, answer

class SearchKeyWord(BaseCheck):
    def __init__(self, presentation, key_slide):
        super().__init__(presentation)
        self.key_slide = key_slide

    def check(self):
        for i, text in enumerate(self.presentation.get_text_from_slides(), 1):
            if self.key_slide.lower() in str(text).lower():
                return answer(True, i, 'Найден под номером: {}'.format(i))
        return answer(False, None, 'Слайд не найден')
