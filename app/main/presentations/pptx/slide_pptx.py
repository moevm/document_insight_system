from pptx.enum.shapes import PP_PLACEHOLDER
from pptx.enum.shapes import MSO_SHAPE_TYPE
from pptx.enum.dml import MSO_FILL

from ..slide_basic import SlideBasic


class SlidePPTX(SlideBasic):
    def __init__(self, container, w, h, index=-1):
        SlideBasic.__init__(self, container)
        self.dimensions = [w, h]
        self.size_of_shape = []
        self.captions = []
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
                if self.text.strip():
                    self.size_of_shape.append((shape.text, shape.top, shape.left, shape.width))
            if shape.has_table:
                self.table.append(shape)

        if self.images:
            sorted_size_of_shape = sorted(self.size_of_shape, key=lambda x:x[1])
            for image in self.images:
                for top in sorted_size_of_shape:              
                    if top[1] > (image.top + image.height):
                        if top[2] > image.left and (top[3]+top[2]) < (image.left+image.width):
                            caption = top[0]
                            self.captions.append(caption)
                            break
                        if abs(top[2] - image.left) < 400000 and abs((top[3]+top[2]) - (image.left+image.width)) < 400000:
                            caption = top[0]
                            self.captions.append(caption)
                            break

    def __str__(self):
        return super().__str__()
