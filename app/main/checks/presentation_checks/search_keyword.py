import re

from ..base_check import BasePresCriterion, answer


class SearchKeyWord(BasePresCriterion):
    label = "Поиск ключевого слова в тексте слайда"
    _description = 'Например, поиск ключевого слова "Актуальность"'
    id = 'find_on_slide'

    def __init__(self, file_info, key_slide):
        super().__init__(file_info)
        if isinstance(key_slide, str):
            key_slide = [key_slide]
        if not key_slide:
            raise ValueError('key_slide не должен быть пустым.')
        self.key_slide = f"({'|'.join((re.escape(key.lower()) for key in key_slide))})"

    def check(self):
        for i, text in enumerate(self.file.get_text_from_slides(), 1):
            if re.search(self.key_slide, str(text).lower()):
                found = self.format_page_link([i])
                return answer(True, 'Найден под номером: {}'.format(', '.join(map(str, found))))
        return answer(False, 'Слайд не найден')

    @property
    def name(self):
        return f"Слайд с упоминанием: {self.key_slide}"
