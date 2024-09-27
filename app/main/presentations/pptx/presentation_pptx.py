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

        images_with_captions = []

        for slide in self.prs.slides:
            for shape in slide.shapes:
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    image_data = shape.image.blob  # Бинарные данные изображения
                    caption = ""

                    # Определение подписи. Предполагается, что подпись находится рядом с изображением
                    if shape.has_text_frame:
                        caption = shape.text.strip()
                    else:
                        # Альтернативный способ: поиск текстового поля рядом с изображением
                        pass

                    # Сохранение изображения и подписи в MongoDB
                    save_image_to_db(check_id, image_data, caption)
                    images_with_captions.append({"image_data": image_data, "caption": caption})

        return images_with_captions