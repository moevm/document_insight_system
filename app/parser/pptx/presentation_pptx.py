from app.parser.pptx.slide_pptx import SlidePPTX
from pptx import Presentation
from app.parser.presentation_basic import PresentationBasic


class PresentationPPTX(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name, [], "", [])
        self.prs = Presentation(presentation_name)
        self.add_slides()

    def add_slides(self):
        for slide in self.prs.slides:
            self.slides.append(SlidePPTX(slide))

    def get_text_from_slides(self):
        for slide in self.slides:
            self.text += slide.get_text()
        return self.text

    def get_titles(self):
        for slide in self.slides:
            self.titles.append(slide.get_title())
        return self.titles

