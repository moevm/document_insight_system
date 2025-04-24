from ..base_check import BaseReportCriterion, answer


class ImageTextCheck(BaseReportCriterion):
    label = "Проверка текста, считанного с изображений"
    description = ''
    id = 'image_text_check'
    # Подобрать значения для symbols_set, max_symbols_percentage, max_text_density
    def __init__(self, file_info, symbols_set=['%', '1'], max_symbols_percentage=0, max_text_density=4):
        super().__init__(file_info)
        self.images = self.file.images
        self.symbols_set = symbols_set
        self.max_symbols_percentage = max_symbols_percentage
        self.max_text_density = max_text_density

    def check(self):
        from app.tesseract_tasks import tesseract_recognize, callback_task
        from db.db_methods import add_celery_tesseract_task
        if self.images:
            tesseract_task = tesseract_recognize.apply_async(
                args=[self.images[0].check_id, self.symbols_set, self.max_symbols_percentage, self.max_text_density],
                link=callback_task.s(self.images[0].check_id),
                link_error=callback_task.s(self.images[0].check_id)
            )
            add_celery_tesseract_task(tesseract_task.id, self.images[0].check_id)
            return answer(True, 'Изображения проверяются!')
        else:
            return answer(True, 'Изображения не найдены!')
