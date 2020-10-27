from app.parser.odp.presentation_odp import PresentationODP
from app.parser.pptx.presentation_pptx import PresentationPPTX


class Parser:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.presentation = None

    def get_presentation_name(self):
        return self.presentation_name

    def parse_presentation(self):
        if str(self.presentation_name).endswith('.ppt') or str(self.presentation_name).endswith('.pptx'):
            self.presentation = PresentationPPTX(self.presentation_name)
            return self.presentation.get_text_from_slides()
        elif str(self.presentation_name).endswith('.odp'):
            self.presentation = PresentationODP(self.presentation_name)
            return self.presentation.get_text_from_slides()
        return ""
