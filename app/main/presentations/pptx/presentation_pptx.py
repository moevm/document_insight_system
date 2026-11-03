from types import SimpleNamespace

from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE

from ..presentation_basic import PresentationBasic
from .slide_pptx import SlidePPTX

EMU_PER_CENTIMETER = 360000


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

    def _find_image_with_caption(self, shapes, image_shape):
        for shape in shapes:
            if not shape.has_text_frame:
                continue
            caption = shape.text.strip()
            if caption:
                return SimpleNamespace(
                    data=image_shape.image.blob,
                    caption=caption,
                    size=(image_shape.width / EMU_PER_CENTIMETER, image_shape.height / EMU_PER_CENTIMETER),
                )
        return None

    def extract_images_with_captions(self, check_id, document_id=None):
        from app.db.methods.image import get_images_by_check_id, save_image_to_db

        self.check_id = str(check_id)
        for slide in self.slides:
            for shape in slide.slide.shapes:
                if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
                    image = self._find_image_with_caption(slide.slide.shapes, shape)
                    if image is None:
                        continue
                    save_image_to_db(
                        check_id,
                        image.data,
                        image.caption,
                        image.size,
                        document_id=document_id,
                    )
        self.images = get_images_by_check_id(check_id)
