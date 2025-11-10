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
                    except (ValueError, TypeError) as exc:
                        self.page_number = [-1, -1, -1]
        if container.shapes.title:
            self.title = container.shapes.title.text

        for shape in container.shapes:
            if hasattr(shape, "image"):
                self.images.append(shape)
            if hasattr(shape, "text"):
                self.text += "\n" + shape.text
                if shape.text.replace(' ', '').replace('<number>', ''): # we replace number of page because it is read as text too
                    self.size_of_shape.append((shape.text, shape.top, shape.left, shape.width))
            if shape.has_table:
                self.table.append(shape)


        if self.images:
            for image in self.images:
                '''
                The next expression finds the most close text for image.
                It is work this way, because a holder for picture and a holder for capture don't strictly correspond in size.
                For example, sometimes the capture holder runs over the picture holder, the text width is always different ect
                '''
                sorted_size_of_shape = sorted(self.size_of_shape,
                                              key=lambda x:(abs(x[1]-(image.top+image.height))+abs(x[2]-image.left) + abs(x[3]+x[2]-(image.left+image.width))))
                self.captions.append(sorted_size_of_shape[0])

    def __str__(self):
        return super().__str__()
