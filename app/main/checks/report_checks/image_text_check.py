from ..base_check import BaseReportCriterion, answer


class ImageTextCheck(BaseReportCriterion):
    label = "Проверка текста, считанного с изображений"
    _description = ''
    id = 'image_text_check'

    def __init__(
        self,
        file_info,
        symbols_set=None,
        max_symbols_percentage=5,
        max_text_density=4,
    ):
        super().__init__(file_info)
        self.images = self.file.images

        if symbols_set is None:
            symbols_set = list("@#$%^&*~`‘|±§№¤¢£€{¥}©®™•¶÷×")

        self.symbols_set = symbols_set
        self.max_symbols_percentage = max_symbols_percentage
        self.max_text_density = max_text_density

    def check(self):
        from app.celery_tasks.tesseract import callback_task, tesseract_recognize
        from app.db.methods.celery_tesseract import add_celery_tesseract_task

        if self.images:
            check_id = self.images[0].active_check_id
            tesseract_task = tesseract_recognize.apply_async(
                args=[
                    check_id,
                    self.symbols_set,
                    self.max_symbols_percentage,
                    self.max_text_density,
                ],
                link=callback_task.si(check_id),
                link_error=callback_task.si(check_id),
            )
            add_celery_tesseract_task(tesseract_task.id, check_id)
            return answer(True, 'Изображения проверяются!')
        else:
            return answer(True, 'Изображения не найдены!')
