import itertools
import re

from utils import format_header

from ..base_check import BasePresCriterion, answer


class TitleFormatCheck(BasePresCriterion):
    description = "Заголовки слайдов присутствуют и занимают не более двух строк"
    id = 'slides_headers'

    def __init__(self, file_info):
        super().__init__(file_info)
        self.empty_headers = []
        self.len_exceeded = []

    def exceeded_verdict(self):
        return format_header(
            'Превышение длины: {}'.format(', '.join(map(str, self.format_page_link(self.len_exceeded))))), \
               format_header('Убедитесь в корректности заголовка и текста слайда')

    def empty_verdict(self):
        return format_header(
            'Заголовки не найдены: {}'.format(', '.join(map(str, self.format_page_link(self.empty_headers))))), \
               format_header(
                   'Убедитесь, что слайд при наведении на него курсора имеет название, соответствующее заголовку на самом слайде.\nДля добавления заглавия в PowerPoint на вкладке Вид нажмите кнопку Режим структуры и щелкните справа от нужного слайда. Затем введите название')

    def get_failing_headers(self):
        for i, title in enumerate(self.file.get_titles(), 1):
            if title == "":
                self.empty_headers.append(i)
                continue

            title = str(title).replace('\x0b', '\n')
            if '\n' in title or '\r' in title:
                titles = [t for t in re.split('\r|\n', title) if t != '']
                if len(titles) > 2:
                    self.len_exceeded.append(i)

        return self.empty_headers, self.len_exceeded

    def check(self):
        self.get_failing_headers()
        error_slides = list(itertools.chain(self.empty_headers, self.len_exceeded))
        if not error_slides:
            return answer(not bool(error_slides), "Пройдена!")
        elif len(self.empty_headers) == 0 and len(self.len_exceeded) != 0:
            return answer(False, *self.exceeded_verdict())
        elif len(self.empty_headers) != 0 and len(self.len_exceeded) == 0:
            return answer(False, *self.empty_verdict())
        else:
            return answer(False,
                          *list(itertools.chain(self.empty_verdict(), self.exceeded_verdict())))
