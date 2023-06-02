
from app.utils.parse_for_html import format_header
from ..base_check import BasePresCriterion, answer


class PresEmptySlideCheck(BasePresCriterion):
    description = "Проверка наличия пустых слайдов в презентации"
    id = 'pres_empty_slide'

    def __init__(self, file_info):
        super().__init__(file_info)

    def check(self):
        empty_pages = []
        for page, slide in enumerate(self.file.get_text_from_slides(), 1):
            if not slide.strip():
                empty_pages.append(page)
        if empty_pages:
            empty_pages = self.format_page_link(empty_pages)
            return answer(False, format_header(
                'Не пройдена, обнаружены пустые слайды: {}'.format(', '.join(map(str, empty_pages)))))
        else:
            return answer(True, "Пройдена!")
