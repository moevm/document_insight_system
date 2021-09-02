from app.main.checks.base_check import BaseCheck, answer

class FindDefSld(BaseCheck):
    def __init__(self, presentation, type_of_slide):
        super().__init__(presentation)
        self.type_of_slide = type_of_slide

    def check(self):
        found_slides, found_idxs  = [], []
        for i, title in enumerate(self.presentation.get_titles(), 1):
            if str(title).lower().find(str(self.type_of_slide).lower()) != -1:
                found_slides.append(self.presentation.get_text_from_slides()[i - 1])
                found_idxs.append(i)
        if len(found_slides) == 0:
            return answer(False, None, 'Слайд не найден'), ''
        else:
            return answer(True, found_idxs, 'Найден под номером: {}'.format(', '.join(map(str, found_idxs)))), ' '.join(found_slides)
