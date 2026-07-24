from unittest.mock import Mock


class MockPresentation:
    def __init__(self):
        self.texts = []
        self.titles = []
        self.found_index = {}
        self.slides = []

    def get_text_from_slides(self):
        return self.texts

    def get_titles(self):
        return self.titles

    def format_page_link(self, indexes):
        return [str(idx + 1) for idx in indexes]