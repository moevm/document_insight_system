from main.reports.docx_uploader.docx_uploader import DocxUploader
from main.presentations import PresentationODP, PresentationPPTX
import logging

from utils.converter import convert_to

logger = logging.getLogger('root_logger')

def parse(filename):
    if filename.endswith('.ppt') or filename.endswith('.pptx'):
        try:
            return PresentationPPTX(filename)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    elif filename.endswith('.odp'):
        try:
            return PresentationODP(filename)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    elif filename.endswith('.doc') or filename.endswith('.odt'):
        try:
            converted_file_path = convert_to(filename, target_format='docx')
            docx = DocxUploader()
            docx.upload(converted_file_path)
            docx.parse()
            return docx
        except Exception as err:
            logger.error(err, exc_info=True)
            return None

    elif filename.endswith('.docx'):
        try:
            docx = DocxUploader()
            docx.upload(filename)
            docx.parse()
            return docx
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    else:
        raise ValueError("Файл с недопустимым именем или недопустимого формата: " + filename)
