from app.parser.pptx.slide_pptx import SlidePPTX
from pptx import Presentation


class PresentationPPTX:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.prs = Presentation(self.presentation_name)
        self.slides = []
        self.text = ""
        self.titles = []

    def add_slides(self):
        for slide in self.prs.slides:
            self.slides.append(SlidePPTX(slide))

    def get_text_from_slides(self):
        if not len(self.slides):
            self.add_slides()
        for slide in self.slides:
            self.text += slide.get_text()
        return self.text

    def get_titles(self):
        if not len(self.slides):
            self.add_slides()
        for slide in self.slides:
            self.titles.append(slide.get_title())
        return self.titles

