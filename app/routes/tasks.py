from os.path import join
from bson import ObjectId
from celery.result import AsyncResult

from flask import Blueprint, request, current_app, jsonify
from flask_login import login_required, current_user
from app.root_logger import get_root_logger

from app.utils import get_file_len, check_file
from app.db.methods import file as file_methods
from app.db.methods import check as check_methods
from app.db.methods import celery_check as celery_check_methods
from app.db.types.Check import Check

from app.server_consts import ALLOWED_EXTENSIONS, UPLOAD_FOLDER
from app.tasks import create_task

tasks = Blueprint('tasks', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@tasks.route("/", methods=["POST"])
@login_required
def run_task():
    file = request.files.get("file")
    pdf_file = request.files.get("pdf_file")
    file_type = request.form.get('file_type', 'pres')
    filename, extension = file.filename.rsplit('.', 1)
    file_ext_type = current_user.file_type['type']

    if not file:
        logger.critical("request doesn't include file")
        return "request doesn't include file"
    if get_file_len(file) * 2 + file_methods.get_storage() > current_app.config['MAX_SYSTEM_STORAGE']:
        logger.critical('Storage overload has occured')
        return 'storage_overload'
    file_check_response = check_file(file, extension, ALLOWED_EXTENSIONS[file_ext_type], check_mime=True)
    if file_check_response != "":
        logger.info('Пользователь загрузил файл с ошибочным расширением: ' + file_check_response)
        return file_check_response

    if pdf_file:
        pdf_file_check_response = check_file(pdf_file, pdf_file.filename.rsplit('.', 1)[1], "pdf", check_mime=True)
        if pdf_file_check_response != "":
            logger.info('Пользователь загрузил файл с ошибочным расширением: pdf_' + pdf_file_check_response)
            return "pdf_" + pdf_file_check_response

    logger.info(
        f"Запуск обработки файла {file.filename} пользователя {current_user.username} с критериями {current_user.criteria}"
    )

    # save to file on disk for future checking
    file_id = ObjectId()
    filepath = join(UPLOAD_FOLDER, f"{file_id}.{extension}")
    file.save(filepath)
    # add file and file's info to db
    file_id = file_methods.add_file_info_and_content(current_user.username, filepath, file_type, file_id)
    # use pdf from response or convert to pdf and save on disk and db
    if current_user.two_files and pdf_file:
        if get_file_len(pdf_file) * 2 + file_methods.get_storage() > current_app.config['MAX_SYSTEM_STORAGE']:
            logger.critical('Storage overload has occured')
            return 'storage_overload'
        logger.info(
            f"Запуск обработки файла {pdf_file.filename} пользователя {current_user.username} с критериями {current_user.criteria}")
        filenamepdf, extension = pdf_file.filename.rsplit('.', 1)
        filepathpdf = join(UPLOAD_FOLDER, f"{file_id}.{extension}")
        pdf_file.save(filepathpdf)
        converted_id = file_methods.add_file_to_db(filenamepdf, filepathpdf)
    else:
        converted_id = file_methods.write_pdf(filename, filepath)
    check = Check({
        '_id': file_id,
        'conv_pdf_fs_id': converted_id,
        'user': current_user.username,
        'lms_user_id': current_user.lms_user_id,
        'enabled_checks': current_user.criteria,
        'criteria': current_user.criteria,
        'file_type': current_user.file_type,
        'filename': file.filename,
        'score': -1,  # score=-1 -> checking in progress
        'is_ended': False,
        'is_failed': False,
        'params_for_passback': current_user.params_for_passback
    })
    check_methods.add_check(file_id, check)  # add check for parsed_file to db
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    celery_check_methods.add_celery_task(task.id, file_id)  # mapping celery_task to check (check_id = file_id)
    return {'task_id': task.id, 'check_id': str(file_id)}


@tasks.route("/<task_id>", methods=["GET"])
@login_required
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return jsonify(result), 200
