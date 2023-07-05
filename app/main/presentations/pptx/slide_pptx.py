from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.dml import MSO_FILL

from ..slide_basic import SlideBasic


class SlidePPTX(SlideBasic):
    def __init__(self, container, w, h, index=-1):
        SlideBasic.__init__(self, container)
        self.dimensions = [w, h]
        for p in container.placeholders:
            if p.is_placeholder and p.placeholder_format.type == PP_PLACEHOLDER.SLIDE_NUMBER:
                if p.text == '‹#›':
                    self.page_number = [index, -1, -1]
                else:
                    try:
                        self.page_number = [int(p.text), int(p.left), int(p.top)]
                    except ValueError:
                        self.page_number = [-1, -1, -1]
        if container.shapes.title:
            self.title = container.shapes.title.text

        for shape in container.shapes:
            if hasattr(shape, "image"):
                self.images.append(shape)
            if hasattr(shape, "text"):
                self.text += "\n" + shape.text
            if shape.has_table:
                self.table.append(shape)

    def __str__(self):
        return super().__str__()
