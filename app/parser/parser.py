from app.parser.odp.presentation_odp import PresentationODP
from app.parser.pptx.presentation_pptx import PresentationPPTX


class Parser:
    def __init__(self, presentation_name):
        self.presentation_name = presentation_name
        self.prs = None

    def get_presentation_name(self):
        return self.presentation_name

    def parse_presentation(self):
        if str(self.presentation_name).endswith('.ppt') or str(self.presentation_name).endswith('.pptx'):
            self.prs = PresentationPPTX(self.presentation_name)
            return self.prs.get_text_from_slides()
        if str(self.presentation_name).endswith('.odp'):
            self.prs = PresentationODP(self.presentation_name)
            return self.prs.get_text_from_slides()
        return ""