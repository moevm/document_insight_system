from ..base_check import BaseReportCriterion, answer
import cv2
import numpy as np
from io import BytesIO

class ReportTaskTracker(BaseReportCriterion):
    label = "Проверка читаемости изображений"
    description = ''
    id = 'image_readability_check'

    def __init__(self, file_info, images, min_laplacian = 100, min_entropy = 5, max_density=10):
        super().__init__(file_info)
        self.images = images # корректно извлечь данные об изображениях
        self.min_laplacian = min_laplacian
        self.min_entropy = min_entropy
        self.max_density = max_density
        self.laplacian_score = None
        self.entropy_score = None

    def late_init(self):
        self.chapters = self.file.make_chapters(self.file_type['report_type'])

    def check(self):
        self.late_init()
        for image in self.images:
            image_array = np.frombuffer(image.image_data, dtype=np.uint8)
            img = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            laplacian, entropy = self.find_params(img)
            width, height = image.image_size
        # проанализровать текст на изображениях
        # дописать сравнение с результатами 
        if False:
            return answer(False, f'Изображения нечитаемы! {self.deny_list}! Обнаруженные слова: {word_in_docs}.')
        else:
            return answer(True, 'Изображения корректны!')

    def find_params(self, image):
        if image is None or image.size == 0:
            return None, None
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        laplacian = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        
        hist, _ = np.histogram(gray_image.flatten(), bins=256, range=[0, 256])
        hist = hist / hist.sum()
        entropy = -np.sum(hist * np.log2(hist + 1e-10))
        return laplacian, entropy
        
    # def analyze_with_pytesseract(image):
    #     try:
    #         if image is None:
    #             raise ValueError("Не удалось загрузить изображение")
    #         text = pytesseract.image_to_string(image, lang='rus+eng')
    #     except Exception as e:
    #         print(f'Ошибка при обработке изображения: {e}')
    #         text = ""

    #     return {
    #         'text': text
    #     }