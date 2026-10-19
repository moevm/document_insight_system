from ..base_check import BaseReportCriterion, answer


class ReportImageShareCheck(BaseReportCriterion):
    label = "Проверка доли объема отчёта, приходящейся на изображения"
    _description = 'Доля изображений (не включая "Приложение") не должна превышать 0,9 и минимального количества'
    id = 'image_share_check'
    warning = True

    def __init__(self, file_info, limit=0.3, min_cnt_img=3):
        super().__init__(file_info)
        self.limit = limit
        self.min_cnt_img = min_cnt_img

    def check(self):
        if not self.has_enough_pages():
            return answer(False, "В отчете недостаточно страниц. Нечего проверять.")
        images_height = self.file.pdf_file.page_images(page_without_pril=self.file.page_count)
        available_space = self.file.pdf_file.page_height(page_without_pril=self.file.page_count)

        images_value = images_height / available_space

        if images_value > self.limit:
            result_str = (
                f'Проверка не пройдена! Изображения в работе занимают около {round(images_value, 2)} объема '
                f'документа без учета приложения, ограничение - {round(self.limit, 2)}'
                """
                    Если доля отчета, приходящаяся на изображения, больше нормы, попробуйте сделать следующее:
                    <ul>
                        <li>Попробуйте перенести малозначимые иллюстрации в Приложение;</li>
                        <li>Если у вас уже есть раздел Приложение, убедитесь, что количество страниц в отчете посчитано программой без учета приложения;</li>
                        <li>Если страницы посчитаны программой неверно, убедитесь, что заголовок приложения правильно оформлен;</li>
                        <li>Убедитесь, что красная строка не сделана с помощью пробелов или табуляции.</li>
                    </ul>
                """
            )
            return answer(False, result_str)
        
        cnt_img = self.file.pdf_file.page_images_count(page_without_pril=self.file.page_count)
        if cnt_img < self.min_cnt_img:
            result_str = (
                f"Проверка не пройдена! Кол-во изображний меньше минимального количества: {cnt_img}/{self.min_cnt_img}"
            )
            return answer(False, result_str)
        
        return answer(True, 'Пройдена!')
