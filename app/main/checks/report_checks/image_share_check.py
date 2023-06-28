from ..base_check import BaseReportCriterion, answer


class ReportImageShareCheck(BaseReportCriterion):
    description = "Проверка доли объема отчёта, приходящейся на изображения"
    id = 'image_share_check'

    def __init__(self, file_info, limit=0.3):
        super().__init__(file_info)
        self.limit = limit

    def check(self):
        if self.file.page_counter() < 4:
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        images_height = 0
        for image in self.file.inline_shapes:
            images_height += image.height.cm
        if len(self.file.file.sections):
            available_space = self.file.file.sections[0].page_height.cm - self.file.file.sections[0].bottom_margin.cm - \
                              self.file.file.sections[0].top_margin.cm
            images_pages = images_height / available_space
            share = images_pages / self.file.count
            if share > self.limit:
                result_str = f'Проверка не пройдена! Изображения в работе занимают около {round(share, 2)} объема ' \
                             f'документа без учета приложения, ограничение - {round(self.limit, 2)}'
                result_str += '''
                            Если доля отчета, приходящаяся на изображения, больше нормы, попробуйте сделать следующее:
                            <ul>
                                <li>Попробуйте перенести малозначимые иллюстрации в Приложение;</li>
                                <li>Если у вас уже есть раздел Приложение, убедитесь, что количество страниц в отчете посчитано программой без учета приложения;</li>
                                <li>Если страницы посчитаны программой неверно, убедитесь, что заголовок приложения правильно оформлен;</li>
                                <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
                            </ul>
                            '''
                return answer(False, result_str)
            else:
                return answer(True, f'Пройдена!')
        return answer(False, 'Во время обработки произошла критическая ошибка')
