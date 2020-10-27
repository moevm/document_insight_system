from app.parser.slide import Slide
from pptx import Presentation
from app.parser.presentation_basic import PresentationBasic


class PresentationPPTX(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name, [], "", [])
        self.prs = Presentation(presentation_name)
        self.add_slides()

    def add_slides(self):
        for slide in self.prs.slides:
            self.slides.append(Slide(slide, 'pptx'))


