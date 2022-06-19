import logging
import tempfile

from main.presentations import PresentationODP, PresentationPPTX
from main.reports.docx_uploader import DocxUploader
from utils import convert_to

logger = logging.getLogger('root_logger')


def parse(filepath):
    if filepath.endswith('.ppt') or filepath.endswith('.pptx'):
        try:
            return PresentationPPTX(filepath)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    elif filepath.endswith('.odp'):
        try:
            return PresentationODP(filepath)
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    elif filepath.endswith('.doc') or filepath.endswith('.odt'):
        try:
            converted_file_path = convert_to(filepath, target_format='docx')
            docx = DocxUploader()
            docx.upload(converted_file_path)
            docx.parse()
            return docx
        except Exception as err:
            logger.error(err, exc_info=True)
            return None

    elif filepath.endswith('.docx'):
        try:
            docx = DocxUploader()
            docx.upload(filepath)
            docx.parse()
            return docx
        except Exception as err:
            logger.error(err, exc_info=True)
            return None
    else:
        raise ValueError("Файл с недопустимым именем или недопустимого формата: " + filename)


def save_to_temp_file(file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file.read())
    temp_file.close()
    file.seek(0)
    return temp_file.name
