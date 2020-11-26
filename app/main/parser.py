from app.main.odp.presentation_odp import PresentationODP
from app.main.pptx.presentation_pptx import PresentationPPTX


def parse(presentation_name):
    if presentation_name.endswith('.ppt') or presentation_name.endswith('.pptx'):
        try:
            return PresentationPPTX(presentation_name)
        except Exception as err:
            print(err)
            return None
    elif presentation_name.endswith('.odp'):
        try:
            return PresentationODP(presentation_name)
        except Exception as err:
            print(err)
            return None
