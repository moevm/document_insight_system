import os

import logging
import tempfile

from main.presentations import PresentationPPTX
from main.reports.docx_uploader import DocxUploader
from utils import convert_to

logger = logging.getLogger('root_logger')


def parse(filepath, pdf_filepath):
    tmp_filepath = filepath.lower()
    try:
        new_filepath = filepath
        if tmp_filepath.endswith('.odp'):
            new_filepath = convert_to(filepath, target_format='pptx')
        elif tmp_filepath.endswith('.ppt') or tmp_filepath.endswith('.pptx'):
            file_object = PresentationPPTX(new_filepath)
        else:
            new_filepath = filepath
            if tmp_filepath.endswith('.doc') or tmp_filepath.endswith('.odt'):
                new_filepath = convert_to(filepath, target_format='docx')
            elif tmp_filepath.endswith('.docx'):
                docx = DocxUploader()
                docx.upload(new_filepath, pdf_filepath)
                docx.parse()
                file_object = docx
        # Если была конвертация, то удаляем временный файл.
        if new_filepath != filepath:
            os.remove(new_filepath)
        return file_object
    except Exception as err:
            logger.error(err, exc_info=True)
            return None


def save_to_temp_file(file):
    temp_file = tempfile.NamedTemporaryFile(delete=False)
    temp_file.write(file.read())
    temp_file.close()
    file.seek(0)
    return temp_file.name
