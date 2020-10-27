from app.parser.odp.presentation_odp import PresentationODP
from app.parser.pptx.presentation_pptx import PresentationPPTX


class Parser:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.presentation = None
        self.state = 0

    def get_presentation_name(self):
        return self.presentation_name

    def parse_presentation(self):
        if str(self.presentation_name).endswith('.ppt') or str(self.presentation_name).endswith('.pptx'):
            try:
                self.presentation = PresentationPPTX(self.presentation_name)
                self.state = 1
                text = self.presentation.get_text_from_slides()
                self.state = 2
                return text
            except Exception as err:
                print(err)
                self.state = -1
        elif str(self.presentation_name).endswith('.odp'):
            try:
                self.presentation = PresentationODP(self.presentation_name)
                self.state = 1
                text = self.presentation.get_text_from_slides()
                self.state = 2
                return text
            except Exception as err:
                print(err)
                self.state = -1
        return ""

    def get_state(self):
        return self.state
