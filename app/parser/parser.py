from app.parser.odp.presentation_odp import PresentationODP
from app.parser.pptx.presentation_pptx import PresentationPPTX


class Parser:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.presentation = None
        self.state = 0
        self.text = []
        self.titles = []
        self.parse_presentation()

    def get_presentation_name(self):
        return self.presentation_name

    def parse_presentation(self):
        if str(self.presentation_name).endswith('.ppt') or str(self.presentation_name).endswith('.pptx'):
            try:
                self.state = 1
                self.presentation = PresentationPPTX(self.presentation_name)
                self.state = 2
                self.text = self.presentation.get_text_from_slides()
                self.titles = self.presentation.get_titles()
                self.state = 3
            except Exception as err:
                print(err)
                self.state = -1
        elif str(self.presentation_name).endswith('.odp'):
            try:
                self.state = 1
                self.presentation = PresentationODP(self.presentation_name)
                self.state = 2
                self.text = self.presentation.get_text_from_slides()
                self.titles = self.presentation.get_titles()
                self.state = 3
            except Exception as err:
                print(err)
                self.state = -1

    def get_titles(self):
        return self.titles

    def get_text(self):
        return self.text

    def get_state(self):
        return self.state
