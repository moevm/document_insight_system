class SlideBasic:
    def __init__(self, container):  # Extracting only the properties we need!
        self.title = ""
        self.text = ""  # Maybe should be a list for multiple text nodes.
        self.page_number = 0

    def get_title(self):
        return self.title

    def get_text(self):
        return self.text

    def get_page_number(self):
        return self.page_number
