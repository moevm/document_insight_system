from io import BytesIO

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from .slide_pptx import SlidePPTX
from ..presentation_basic import PresentationBasic


class PresentationPPTX(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name)
        self.prs = Presentation(presentation_name)
        self.add_slides()
        self.found_index = {}

    def add_slides(self):
        for index, slide in enumerate(self.prs.slides, 1):
            self.slides.append(SlidePPTX(slide, self.prs.slide_width, self.prs.slide_height, index))

    def __str__(self):
        return super().__str__()

    def extract_images_with_captions(self, check_id):
        from app.db.db_methods import save_image_to_db

        # Проход по каждому слайду в презентации
        for slide in self.slides:
            image_found = False
            image_data = None
            caption_text = None

            # Проход по всем фигурам на слайде
            for shape in slide.slide.shapes:  # Используем slide.slide для доступа к текущему слайду
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    image_found = True
                    image_part = shape.image  # Получаем объект изображения

                    # Извлекаем бинарные данные изображения
                    image_stream = image_part.blob
                    image_data = BytesIO(image_stream)

                # Если мы нашли изображение, ищем следующий непустой текст как подпись
                if image_found:
                    for shape in slide.slide.shapes:
                        if not shape.has_text_frame:
                            continue
                        text = shape.text.strip()
                        if text:  # Находим непустое текстовое поле (предположительно, это подпись)
                            caption_text = text
                            # Сохраняем изображение и его подпись
                            save_image_to_db(check_id, image_data.getvalue(), caption_text)
                            break  # Предполагаем, что это подпись к текущему изображению

                    # Сброс флага и данных изображения для следующего цикла
                    image_found = False
                    image_data = None
                    caption_text = None
