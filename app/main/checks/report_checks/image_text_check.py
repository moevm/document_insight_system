import re
from ..base_check import BaseReportCriterion, answer
import time
from celery.result import AsyncResult

class ImageTextCheck(BaseReportCriterion):
    label = "Проверка текста, считанного с изображений"
    description = ''
    id = 'image_text_check'
    # Подобрать значения для symbols_set, max_symbols_percentage, max_text_density
    def __init__(self, file_info, symbols_set=['%', '1'], max_symbols_percentage=0, max_text_density=0, max_wait_time=30):
        super().__init__(file_info)
        self.images = self.file.images
        self.symbols_set = symbols_set
        self.max_symbols_percentage = max_symbols_percentage
        self.max_text_density = max_text_density
        self.max_wait_time = max_wait_time

    def check(self):
        deny_list = []
        if self.images:
            for image in self.images:
                if image.text == '':
                    continue
                recognized_text = self.wait_for_text_recognition(image)
                width, height = image.image_size
                if not recognized_text:
                    continue
                text_density = self.calculate_text_density(recognized_text, width, height)
                if text_density > self.max_text_density:
                    deny_list.append(
                        f"Изображение с подписью '{image.caption}' имеет слишком высокую плотность текста: "
                        f"{text_density:.4f} (максимум {self.max_text_density}). Это может означать, что текст нечитаем.<br>"
                    )
                symbols_count = self.count_symbols_in_text(recognized_text, self.symbols_set)
                text_length = len(recognized_text)
                symbols_percentage = (symbols_count / text_length) * 100
                if symbols_percentage > self.max_symbols_percentage:
                    deny_list.append(
                        f"На изображении с подписью '{image.caption}' содержится слишком много неверно распознанных символов: "
                        f"{symbols_percentage:.2f}% (максимум {self.max_symbols_percentage}%). Это может означать, что размер шрифта слишком маленький или текст нечитаем.<br>"
                    )
        else:
            return answer(False, 'Изображения не найдены!')
        if deny_list:
            return answer(False, f'Проблемы с текстом на изображениях! <br>{"".join(deny_list)}')
        else:
            return answer(True, 'Текст на изображениях корректен!')

    def count_symbols_in_text(self, text, symbols_set):
        return sum(1 for char in text if char in symbols_set)

    def calculate_text_density(self, text, width, height):
        text_without_spaces = ''.join(text.split())
        image_area = width * height
        if image_area == 0:
            return 0
        return len(text_without_spaces) / image_area

    def wait_for_text_recognition(self, image):
        from app.db.db_methods import add_image_text
        start_time = time.time()
        task_id = image.tesseract_task_id
        if not task_id:
            return None

        while time.time() - start_time < self.max_wait_time:
            task_result = AsyncResult(task_id)
            if task_result.state == 'SUCCESS':
                recognized_text = task_result.result
                recognized_text = re.sub(r'\s+', ' ', recognized_text)
                image.text = recognized_text
                add_image_text(task_id, recognized_text)
                return recognized_text.strip()
            time.sleep(1)

        return None
