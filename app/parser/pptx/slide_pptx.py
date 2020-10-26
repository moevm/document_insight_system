class SlidePPTX:
    def __init__(self, slide):
        self.slide = slide
        self.title = ""
        self.text = ""
        self.page_number = 0

    def parse_slide(self):
        for shape in self.slide.shapes:
            self.title = self.slide.shapes.title.text
            if hasattr(shape, "text"):
                self.text = shape.text

    def get_title(self):
        if self.title == "":
            self.parse_slide()
        return self.title

    def get_text(self):
        if self.text == "":
            self.parse_slide()
        return self.text

    def get_page_number(self):
        return self.page_number