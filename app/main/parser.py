from app.main.mse22.converter_to_docx.converted_parser import ConvertedParser
from app.main.mse22.docx_uploader.docx_uploader import DocxUploader
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
    elif presentation_name.endswith('.doc'):
        try:
            doc = ConvertedParser()
            doc.parse(presentation_name)
            doc.parcing()
            return str(doc)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None

    elif presentation_name.endswith('.docx'):
        try:
            docx = DocxUploader()
            docx.upload_from_cli(presentation_name)
            docx.parcing()
            return str(docx)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None

    elif presentation_name.endswith('.odt'):
        try:
            odt = ConvertedParser()
            odt.parse(presentation_name)
            odt.parcing()
            return str(odt)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    else:
        raise ValueError("Файл с недопустимым именем или недопустимого формата: " + presentation_name)
