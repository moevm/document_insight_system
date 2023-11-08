class SlideBasic:
    def __init__(self, container):  # Extracting only the properties we need!
        self.title = ""
        self.text = ""  # Maybe should be a list for multiple text nodes.
        self.page_number = [-1, -1, -1]
        self.dimensions = [-1, -1]
        self.images = []
        self.table = []

    def get_title(self):
        return self.title

    def get_text(self):
        return self.text

    def get_page_number(self):
        return self.page_number
        
    def get_images(self):
        return self.images

    def get_table(self):
        return self.table

    def __str__(self):
        return f"\tTitle: {self.title}.\n\tText: {self.text}.\n\tPage_num: {self.page_number}"
