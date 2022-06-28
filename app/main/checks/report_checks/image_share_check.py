from ..base_check import BaseCheck, answer


class ReportImageShareCheck(BaseCheck):
    def __init__(self, file, limit = 2):
        super().__init__(file)
        self.limit = limit

    def check(self):
        images_height = 0
        for image in self.file.inline_shapes:
            images_height += image.height.cm
        if len(self.file.file.sections):
            pages = round(images_height / self.file.file.sections[0].page_height.cm)
            if pages > self.limit:
                return answer(False, f'Проверка не пройдена! Изображения в работе занимают около {pages} страниц, ограничение - {self.limit}')
            else:
                return answer(True, f'Проверка пройдена!')
        return answer(False, 'Во время обработки произошла критическая ошибка')
