from app.main.slide_basic import SlideBasic
from pptx.enum.shapes import PP_PLACEHOLDER


class SlidePPTX(SlideBasic):
    def __init__(self, container, w, h):
        SlideBasic.__init__(self, container)
        self.dimensions = [w, h]
        for p in container.placeholders:
            if p.is_placeholder and p.placeholder_format.type == PP_PLACEHOLDER.SLIDE_NUMBER:
                self.page_number = [int(p.text), int(p.left), int(p.top)]
        for shape in container.shapes:
            self.title = container.shapes.title.text  # Bug! Not all slides have title!
            if hasattr(shape, "text"):
                self.text = shape.text  # Is it possible for .PPTX presentation to have more than one text node on a single slide?
