from ..base_check import answer, BasePresCriterion


class FindDefSld(BasePresCriterion):
    label = "Поиск ключевого слова в заголовках"
    description = 'Поиск ключевого слова в заголовках'
    id = 'find_slides'

    def __init__(self, file_info, key_slide):
        super().__init__(file_info)
        self.type_of_slide = key_slide
        self.found_idxs = []

    def check(self):
        if self.file is not None:
            for i, title in enumerate(self.file.get_titles(), 1):
                if str(title).lower().find(str(self.type_of_slide).lower()) != -1:
                    #found_slides.append(self.file.get_text_from_slides()[i - 1])
                    self.found_idxs.append(i)
        
        # save fot future
            self.file.found_index[str(self.type_of_slide)] = self.found_idxs.copy()
        
            if self.found_idxs:
                return answer(True, 'Найден под номером: {}'.format(', '.join(map(str, self.format_page_link(self.found_idxs)))))
            else:
                return answer(False, 'Слайд не найден')

    @property
    def name(self):
        return f"Слайд: '{self.type_of_slide}'"
