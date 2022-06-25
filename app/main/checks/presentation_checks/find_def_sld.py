from ..base_check import BaseCheck, answer


class FindDefSld(BaseCheck):
    def __init__(self, file_info, type_of_slide):
        super().__init__(file_info)
        self.type_of_slide = type_of_slide

    def check(self):
        found_slides, found_idxs = [], []
        for i, title in enumerate(self.file.get_titles(), 1):
            if str(title).lower().find(str(self.type_of_slide).lower()) != -1:
                found_slides.append(self.file.get_text_from_slides()[i - 1])
                found_idxs.append(i)
        if len(found_slides) == 0:
            return answer(False, 'Слайд не найден')
        else:
            found_idxs = self.format_page_link(found_idxs)
            return answer(True, 'Найден под номером: {}'.format(', '.join(map(str, found_idxs))))
