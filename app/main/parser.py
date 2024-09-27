import os

import logging
import tempfile

from main.presentations import PresentationPPTX
from main.reports.docx_uploader import DocxUploader
from main.reports.md_uploader import MdUploader
from utils import convert_to

from os.path import basename
from app.db.db_methods import add_check
from app.db.db_types import Check

logger = logging.getLogger('root_logger')

def parse(filepath, pdf_filepath):
    tmp_filepath = filepath.lower()
    try:
        if tmp_filepath.endswith(('.odp', '.ppt', '.pptx')):
            new_filepath = filepath
            if tmp_filepath.endswith(('.odp', '.ppt')):
                logger.info(f"Презентация {filepath} старого формата. Временно преобразована в pptx для обработки.")
                new_filepath = convert_to(filepath, target_format='pptx')

            presentation = PresentationPPTX(new_filepath)

            check = Check({
                'filename': basename(new_filepath),
            })
            check_id = add_check(23, check)
            presentation.extract_images_with_captions(check_id)
            file_object = presentation


        elif tmp_filepath.endswith(('.doc', '.odt', '.docx', )):
            new_filepath = filepath
            if tmp_filepath.endswith(('.doc', '.odt')):
                logger.info(f"Отчёт {filepath} старого формата. Временно преобразован в docx для обработки.")
                new_filepath = convert_to(filepath, target_format='docx')

            docx = DocxUploader()
            docx.upload(new_filepath, pdf_filepath)
            # Создание проверки
            check = Check({
                'filename': basename(new_filepath),
            })
            check_id = add_check(23, check)
            docx.parse()
            docx.extract_images_with_captions(check_id)
            file_object = docx

        elif tmp_filepath.endswith('.md' ):
            new_filepath = filepath
            doc = MdUploader(new_filepath)
            md_text = doc.upload()
            doc.parse(md_text)
            file_object = doc

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