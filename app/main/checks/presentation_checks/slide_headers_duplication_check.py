from ..base_check import BasePresCriterion, answer


class SlideHeadersDuplicationCheck(BasePresCriterion):
    label = "Заголовки слайдов не дублируются"
    description = 'Проверка на дублируемость заголовков слайдов'
    id = 'slide_headers_duplication_check'

    def __init__(self, file_info):
        super().__init__(file_info)

    def get_duplication_headers(self):
        headers = {}
        for slide, key in enumerate(self.file.get_titles(), 1):
            if key in headers:
                headers[key].append(slide)
            else:
                headers[key] = [slide]
        return headers

    def check(self):
        headers = self.get_duplication_headers()
        result_str = ""
        for key, slide in headers.items():
            if len(slide) > 1:
                links = self.format_page_link(slide)
                result_str += f'- "{key}": слайды {links};<br>'
        if not result_str:
            return answer(True, 'Пройдена!')
        else:
            result_str = "Заголовки слайдов не должны быть одинаковыми:<br>" + result_str
            result_str += f'<br>Примечание: в крайнем случае, если без дублирования не обойтись (например, одна задача размещена на нескольких слайдах), добавьте цифры 1,2,3 к названиям: "Проектирование системы 1", "Проектирование системы 2"'
            return answer(False, result_str)
