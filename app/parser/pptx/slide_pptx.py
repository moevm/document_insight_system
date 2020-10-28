from app.parser.slide_basic import SlideBasic


class SlidePPTX(SlideBasic):
    def __init__(self, container):
        SlideBasic.__init__(self, container)
        for shape in container.shapes:
            self.title = container.shapes.title.text
            if hasattr(shape, "text"):
                self.text = shape.text  # Is it possible for .PPTX presentation to have more than one text node on a single slide?
