class PresentationBasic:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.slides = []

    def add_slides(self):
        pass

    def get_text_from_slides(self):
        texts = []
        for slide in self.slides:
            text = str(slide.get_text()).replace('\x0b', '\n') + '\n'
            texts.append(text)
        return texts

    def get_titles(self):
        titles = []
        for slide in self.slides:
            titles.append(slide.get_title())
        return titles
