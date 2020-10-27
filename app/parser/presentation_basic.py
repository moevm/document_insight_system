class PresentationBasic:
    def __init__(self, presentation_name, slides, text, titles):
        self.presentation_name = presentation_name
        self.slides = slides
        self.text = text
        self.titles = titles

    def add_slides(self):
        pass

    def get_text_from_slides(self):
        for slide in self.slides:
            self.text += str(slide.get_text()) + '\n'
        return self.text

    def get_titles(self):
        for slide in self.slides:
            self.titles.append(slide.get_title())
        return self.titles
