class Slide:
    def __init__(self, slide, ext):
        self.slide = slide
        self.title = ""
        self.text = ""
        self.page_number = 0
        self.ext = ext
        self.parse_slide()

    def parse_slide(self):
        if self.ext == 'ppt' or self.ext == 'pptx':
            for shape in self.slide.shapes:
                self.title = self.slide.shapes.title.text
                if hasattr(shape, "text"):
                    self.text = shape.text
        elif self.ext == 'odp':
            self.title = self.slide.childNodes[0]
            self.text = self.slide.childNodes[1]

    def get_title(self):
        return self.title

    def get_text(self):
        return self.text

    def get_page_number(self):
        return self.page_number
