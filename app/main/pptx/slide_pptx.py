from app.main.slide_basic import SlideBasic
from pptx.enum.shapes import PP_PLACEHOLDER


class SlidePPTX(SlideBasic):
    def __init__(self, container, w, h):
        SlideBasic.__init__(self, container)
        self.dimensions = [w, h]
        for p in container.placeholders:
            if p.is_placeholder and p.placeholder_format.type == PP_PLACEHOLDER.SLIDE_NUMBER:
                try:
                    self.page_number = [int(p.text), int(p.left), int(p.top)]
                except ValueError:
                    self.page_number = [-1, -1, -1]
        for shape in container.shapes:
            if container.shapes.title:
                self.title = container.shapes.title.text
            else:
                continue
            if hasattr(shape, "text"):
                self.text += "\n" + shape.text
