from app.main.odp.presentation_odp import PresentationODP
from app.main.pptx.presentation_pptx import PresentationPPTX
import logging
logger = logging.getLogger('root_logger')

def parse(presentation_name):
    if presentation_name.endswith('.ppt') or presentation_name.endswith('.pptx'):
        try:
            return PresentationPPTX(presentation_name)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    elif presentation_name.endswith('.odp'):
        try:
            return PresentationODP(presentation_name)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    else:
        raise ValueError("Презентация с недопустимым именем или недопустимого формата: " + presentation_name)
