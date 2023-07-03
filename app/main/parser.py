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
        if tmp_filepath.endswith(('.odp', '.ppt', '.pptx')):
            new_filepath = filepath
            if tmp_filepath.endswith(('.odp', '.ppt')):
                logger.info(f"Презентация {filepath} старого формата. Временно преобразована в pptx для обработки.")
                new_filepath = convert_to(filepath, target_format='pptx')
            file_object = PresentationPPTX(new_filepath)
        elif tmp_filepath.endswith(('.doc', '.odt', '.docx')):
            new_filepath = filepath
            if tmp_filepath.endswith(('.doc', '.odt')):
                logger.info(f"Отчёт {filepath} старого формата. Временно преобразован в docx для обработки.")
                new_filepath = convert_to(filepath, target_format='docx')
            docx = DocxUploader()
            docx.upload(new_filepath, pdf_filepath)
            docx.parse()
            file_object = docx
        else:
            raise ValueError("Файл с недопустимым именем или недопустимого формата: " + filepath)
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
