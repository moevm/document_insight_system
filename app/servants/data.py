from os import remove
from os.path import join, exists
from bson import ObjectId
from flask_login import current_user

from app.bd_helper.bd_helper import *
from app.main.checker import check, parse_check
from app.main.parser import parse
from app.utils.get_file_len import get_file_len
from flask import current_app

import os
import logging
logger = logging.getLogger('root_logger')

def upload(request, upload_folder):
    try:
        file = request.files["presentation"]
        if get_file_len(file)*2 + get_storage() > current_app.config['MAX_SYSTEM_STORAGE']:
            logger.critical('Storage overload has occured')
            return 'storage_overload'
        try:
            converted_id = write_pdf(file)
        except TypeError:
            return 'Not OK, pdf converter refuses connection. Try reloading.'

        filename = join(upload_folder, file.filename)
        file.save(filename)
        delete = True

        presentation_name = basename(filename)
        logger.info("Обработка презентации " + presentation_name + " пользователя " +
              current_user.username + " проверками " + str(current_user.criteria))
        presentation = find_presentation(current_user, presentation_name)
        if presentation is None:
            user, presentation_id = add_presentation(current_user, presentation_name)
            presentation = get_presentation(presentation_id)

        checks = create_check(current_user)

        checks.conv_pdf_fs_id = converted_id
        if filename.endswith('.docx') or filename.endswith('.doc') or filename.endswith('.odt'):
            checks = parse_check(parse(filename), checks, presentation_name)
        else:
            check(parse(filename), checks, presentation_name)
        presentation, checks_id = add_check(presentation, checks, filename)

        if delete and exists(filename):
            remove(filename)

        logger.info("\tОбработка завершена успешно!")
        return str(checks_id)
    except Exception as e:
        logger.error("\tПри обработке произошла ошибка: " + str(e), exc_info=True)
        return 'Not OK, error: {}'.format(e)
