from os import remove
from os.path import join, exists
from flask_login import current_user

from app.bd_helper.bd_helper import *
from app.main.checker import check, check_report
from app.main.parser import parse
from app.utils.get_file_len import get_file_len
from flask import current_app

import logging

from main.reports.document import Document

logger = logging.getLogger('root_logger')

def upload(request, upload_folder):
    try:
        file = request.files["file"]
        file_type = request.form.get('file_type', 'pres')
        if get_file_len(file)*2 + get_storage() > current_app.config['MAX_SYSTEM_STORAGE']:
            logger.critical('Storage overload has occured')
            return 'storage_overload'
        try:
            converted_id = write_pdf(file)
        except TypeError as exc:
            logger.error(exc, exc_info=True)
            return 'Not OK, pdf converter refuses connection. Try reloading.'

        filename = basename(file.filename)
        filepath = join(upload_folder, filename)
        file.save(filepath)

        logger.info("Обработка файла " + filename + " пользователя " +
              current_user.username + " проверками " + str(current_user.criteria))

        file_id = add_presentation(current_user, filename, file_type)
        checking_file = get_presentation(file_id)

        checks = create_check(current_user, file_type)
        checks.conv_pdf_fs_id = converted_id

        if file_type == 'report':
            parsed_file = parse(filepath) # DocxUploader
            checks = check_report(parsed_file, checks, filename)
        else:
            checks = check(parse(filepath), checks, filename)

        checks_id = add_check(checking_file, checks, filepath)

        if exists(filepath): remove(filepath)

        logger.info("\tОбработка завершена успешно!")
        return str(checks_id)
    except Exception as e:
        logger.error("\tПри обработке произошла ошибка: " + str(e), exc_info=True)
        return 'Not OK, error: {}'.format(e)
