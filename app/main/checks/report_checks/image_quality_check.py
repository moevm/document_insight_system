from ..base_check import BaseReportCriterion, answer
import cv2
import numpy as np

class ImageQualityCheck(BaseReportCriterion):
    label = "Проверка качества изображений"
    description = ''
    id = 'image_quality_check'
    # необходимо подобрать min_laplacian и min_entropy
    def __init__(self, file_info, min_laplacian=100, min_entropy=1):
        super().__init__(file_info)
        self.images = self.file.images
        self.min_laplacian = min_laplacian
        self.min_entropy = min_entropy
        self.laplacian_score = None
        self.entropy_score = None

    def check(self):
        deny_list = []
        if self.images:
            for img in self.images:
                image_array = np.frombuffer(img.image_data, dtype=np.uint8)
                img_cv = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
                
                if img_cv is None:
                    deny_list.append(f"Изображение с подписью '{img.caption}' не может быть обработано.<br>")
                    continue
                
                self.find_params(img_cv)
                
                if self.laplacian_score is None or self.entropy_score is None:
                    deny_list.append(f"Изображение с подписью '{img.caption}' не может быть обработано.<br>")
                    continue
                
                if self.laplacian_score < self.min_laplacian:
                    deny_list.append(f"Изображение с подписью '{img.caption}' имеет низкий показатель лапласиана: {self.laplacian_score:.2f} (минимум {self.min_laplacian:.2f}).<br>")
                
                if self.entropy_score < self.min_entropy:
                    deny_list.append(f"Изображение с подписью '{img.caption}' имеет низкую энтропию: {self.entropy_score:.2f} (минимум {self.min_entropy:.2f}).<br>")
        else: 
            return answer(True, 'Изображения не найдены!')
        if deny_list:
            return answer(False, f'Изображения нечитаемы! <br>Попробуйте улучшить качество изображений, возможно они слишком размыты или зашумлены.<br>{"".join(deny_list)}')
        else:
            return answer(True, 'Изображения корректны!')

    def find_params(self, image):
        if image is None or image.size == 0:
            return None, None
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        self.laplacian_score = cv2.Laplacian(gray_image, cv2.CV_64F).var()
        hist, _ = np.histogram(gray_image.flatten(), bins=256, range=[0, 256])
        hist = hist / hist.sum()
        self.entropy_score = -np.sum(hist * np.log2(hist + 1e-10))