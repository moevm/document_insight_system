from app.parser.odp.slide_odp import SlideODP
from app.parser.presentation_basic import PresentationBasic
from odf import opendocument, draw


class PresentationODP(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name)
        self.prs = opendocument.load(presentation_name)
        self.add_slides()

    def add_slides(self):
        for slide in self.prs.getElementsByType(draw.Page):
            self.slides.append(SlideODP(slide))
