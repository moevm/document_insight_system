from pptx import Presentation

from .slide_pptx import SlidePPTX
from ..presentation_basic import PresentationBasic


class PresentationPPTX(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name)
        self.prs = Presentation(presentation_name)
        self.add_slides()

    def add_slides(self):
        for index, slide in enumerate(self.prs.slides, 1):
            self.slides.append(SlidePPTX(slide, self.prs.slide_width, self.prs.slide_height, index))

    def __str__(self):
        return super().__str__()
