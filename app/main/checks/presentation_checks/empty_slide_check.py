import re

from app.utils.parse_for_html import format_header
from ..base_check import BasePresCriterion, answer


class PresEmptySlideCheck(BasePresCriterion):
    description = "Проверка наличия пустых слайдов в презентации"
    id = 'pres_empty_slide'

    def __init__(self, file_info, status=False):
        super().__init__(file_info)
        self.status = status

    def check(self):
        result_str = ''
        page_titles = {}
        full_pages = {}
        empty_pages = []
        pages_with_title = []

        pages_with_images = [page for page, slide in enumerate(self.file.slides, 1)
                             if slide.get_images() or slide.get_table()]

        for page, slide in enumerate(self.file.get_text_from_slides(), 1):
            slide_string = ''.join(slide.replace("\n", " "))
            slide_without_page = re.sub(r'\d+(?=\s*$)', '', slide_string)
            full_pages[str(page)] = ''.join(char for char in slide_without_page.strip() if char.isprintable())
            if not full_pages[str(page)]:
                empty_pages.append(page)

        for page, slide in enumerate(self.file.get_titles(), 1):
            page_titles[str(page)] = slide
            if slide != "Запасные слайды":
                if slide == full_pages[str(page)] and page not in pages_with_images and page not in empty_pages:
                    pages_with_title.append(page)

        if self.file.presentation_name.endswith('.ppt') or self.file.presentation_name.endswith('.pptx'):

            if empty_pages and not pages_with_title:
                result_str += format_header(
                    'Не пройдена! Обнаружены пустые слайды: {}'.format(
                        ', '.join(self.format_page_link(empty_pages)))
                )
            if pages_with_title and not empty_pages:
                result_str += format_header(
                    'Не пройдена! Обнаружены слайды, в которых присутствует только заголовок: {}'.format(
                        ', '.join(self.format_page_link(pages_with_title)))
                )
            if empty_pages and pages_with_title:
                result_str += format_header(
                    'Не пройдена! Обнаружены пустые слайды: {}, также обнаружены слайды, в которых присутствует только заголовок: {}'.format(
                        ', '.join(self.format_page_link(empty_pages)), ', '.join(self.format_page_link(pages_with_title)))
                )
        elif self.file.presentation_name.lower().endswith('.odp'):
            if empty_pages:
                result_str += format_header(
                    'Не пройдена! Обнаружены пустые слайды или слайды, в которых присутствует только заголовок: {}'.format(
                        ', '.join(self.format_page_link(empty_pages)))
                )

        if not result_str:
            self.status = True
            result_str = 'Пройдена!'

        return answer(self.status, result_str)
