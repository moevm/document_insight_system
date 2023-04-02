from odf import opendocument, draw

from app.utils import tict
from .slide_odp import SlideODP
from ..presentation_basic import PresentationBasic


class PresentationODP(PresentationBasic):
    def __init__(self, presentation_name):
        PresentationBasic.__init__(self, presentation_name)
        self.auto_styles = {}
        self.prs = opendocument.load(presentation_name)
        self.parse_styles()
        self.add_slides()

    def add_slides(self):
        for slide in self.prs.getElementsByType(draw.Page):
            self.slides.append(SlideODP(slide, self.auto_styles))

    def parse_styles(self):
        for style in self.prs.automaticstyles.childNodes:
            style_name = tict.get(style.attributes, "name")
            style_params = {}
            for child in style.childNodes:
                style_params.update(tict.dictify(child.attributes))
            self.auto_styles[style_name] = style_params

    def __str__(self):
        return super().__str__()
