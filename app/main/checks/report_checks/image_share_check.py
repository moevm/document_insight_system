from ..base_check import BaseReportCriterion, answer


class ReportImageShareCheck(BaseReportCriterion):
    description = "Проверка доли объема отчёта, приходящейся на изображения"
    id = 'image_share_check'

    def __init__(self, file_info, limit = 0.3):
        super().__init__(file_info)
        self.limit = limit

    def check(self):
        images_height = 0
        for image in self.file.inline_shapes:
            images_height += image.height.cm
        if len(self.file.file.sections):
            available_space = self.file.file.sections[0].page_height.cm - self.file.file.sections[0].bottom_margin.cm - self.file.file.sections[0].top_margin.cm
            images_pages = images_height / available_space
            share = images_pages / self.file.pdf_file.page_count
            if share > self.limit:
                return answer(False, f'Проверка не пройдена! Изображения в работе занимают около {round(share, 2)} объема документа, \
                                        ограничение - {round(self.limit, 2)}')
            else:
                return answer(True, f'Проверка пройдена!')
        return answer(False, 'Во время обработки произошла критическая ошибка')
