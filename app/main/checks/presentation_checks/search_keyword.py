import re

from ..base_check import BaseCheck, answer


class SearchKeyWord(BaseCheck):
    def __init__(self, file_info, key_slide):
        super().__init__(file_info)
        self.key_slide = f"({'|'.join((key.lower() for key in key_slide))})"

    def check(self):
        for i, text in enumerate(self.file.get_text_from_slides(), 1):
            if re.search(self.key_slide, str(text).lower()):
                found = self.format_page_link([i])
                return answer(True, 'Найден под номером: {}'.format(', '.join(map(str, found))))
        return answer(False, 'Слайд не найден')
