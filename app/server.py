import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from os.path import join
from sys import argv
from io import StringIO

import bson
import pandas as pd
from bson import ObjectId
from celery.result import AsyncResult
from flask import (Flask, Response, abort, jsonify, redirect, render_template,
                   request, url_for)
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from flask_recaptcha import ReCaptcha

import servants.user as user
from app.utils import format_check_for_table, check_file
from db import db_methods
from db.db_types import Check
from lti_session_passback.lti import utils
from lti_session_passback.lti.check_request import check_request
from main.check_packs import BASE_PACKS, BaseCriterionPack, DEFAULT_REPORT_TYPE_INFO, DEFAULT_TYPE, REPORT_TYPES, \
    init_criterions
from root_logger import get_logging_stdout_handler, get_root_logger
from servants import pre_luncher
from tasks import create_task
from utils import checklist_filter, decorator_assertion, get_file_len, format_check

logger = get_root_logger('web')
UPLOAD_FOLDER = '/usr/src/project/files'
ALLOWED_EXTENSIONS = {
    'pres': {'ppt', 'pptx', 'odp'},
    'report': {'doc', 'odt', 'docx'}
}
DOCUMENT_TYPES = {'Лабораторная работа', 'Курсовая работа', 'ВКР'}
TABLE_COLUMNS = ['Solution', 'User', 'File', 'Criteria', 'Check added', 'LMS date', 'Score']
URL_DOMEN = os.environ.get('URL_DOMEN', f"http://localhost:{os.environ.get('WEB_PORT', 8080)}")

app = Flask(__name__, static_folder="./../src/", template_folder="./templates/")
app.config.from_pyfile('settings.py')
app.recaptcha = ReCaptcha(app=app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CELERY_RESULT_BACKEND'] = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
app.config['CELERY_BROKER_URL'] = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")

app.logger.addHandler(get_logging_stdout_handler())
app.logger.propagate = False
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db_methods.get_user(user_id)


# User chapters req handlers:
@app.route('/lti', methods=['POST'])
def lti():
    if check_request(request):
        temporary_user_params = request.form
        username = temporary_user_params.get('ext_user_username')
        person_name = utils.get_person_name(temporary_user_params)
        user_id = f"{username}_{temporary_user_params.get('tool_consumer_instance_guid', '')}"
        lms_user_id = temporary_user_params.get('user_id', '')
        params_for_passback = utils.extract_passback_params(temporary_user_params)
        custom_params = utils.get_custom_params(temporary_user_params)

        # task settings
        # pack name
        custom_criterion_pack = custom_params.get('pack', BASE_PACKS.get(DEFAULT_TYPE).name)
        criterion_pack_info = db_methods.get_criteria_pack(custom_criterion_pack)
        if not criterion_pack_info:
            default_criterion_pack = BASE_PACKS.get(DEFAULT_TYPE).name
            logger.error(
                f"Ошибка при lti-авторизации. Несуществующий набор {custom_criterion_pack} пользователя {username}. Установлен набор по умолчанию: {default_criterion_pack}")
            logger.debug(f"lti-параметры: {temporary_user_params}")
            custom_criterion_pack = default_criterion_pack
            criterion_pack_info = db_methods.get_criteria_pack(custom_criterion_pack)
        custom_criterion_pack_obj = BaseCriterionPack(**criterion_pack_info)
        # get file type and formats from pack
        file_type_info = custom_criterion_pack_obj.file_type
        file_type = file_type_info['type']
        two_files = bool(custom_params.get('two_files'))
        formats = sorted((set(map(str.lower, custom_params.get('formats', '').split(','))) & ALLOWED_EXTENSIONS[
            file_type] or ALLOWED_EXTENSIONS[file_type]))

        role = utils.get_role(temporary_user_params)

        logout_user()

        lti_user = db_methods.add_user(user_id, is_LTI=True)
        if lti_user:
            lti_user.name = person_name
            lti_user.is_admin = role
        else:
            lti_user = db_methods.get_user(user_id)

        # task settings
        lti_user.file_type = file_type_info
        lti_user.two_files = two_files
        lti_user.formats = formats
        lti_user.criteria = custom_criterion_pack
        # passback settings
        lti_user.params_for_passback = params_for_passback
        lti_user.lms_user_id = lms_user_id

        db_methods.edit_user(lti_user)

        login_user(lti_user)
        return redirect(url_for('upload'))
    else:
        abort(403)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("./login.html", navi_upload=False)
    elif request.method == "POST":
        u = user.login(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""


@decorator_assertion(app.route("/signup", methods=["GET", "POST"]), app.config["SIGNUP_PAGE_ENABLED"])
def signup():
    if request.method == "GET":
        return render_template("./signup.html", navi_upload=False)
    elif request.method == "POST":
        u = user.signup(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""


@app.route("/user", methods=["GET", "PUT", "DELETE"])
@login_required
def interact():
    if request.method == "GET":
        return user.logout()
    elif request.method == "PUT":
        return user.edit(request.json)


# Main chapters req handlers:

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if current_user.is_LTI or True:  # app.recaptcha.verify(): - disable captcha (cause no login)
            return run_task()
        else:
            abort(401)
    elif request.method == "GET":
        formats = set(current_user.formats)
        file_type = current_user.file_type['type']
        formats = formats & ALLOWED_EXTENSIONS[file_type] if formats else ALLOWED_EXTENSIONS[file_type]
        return render_template("./upload.html", navi_upload=False, formats=sorted(formats))


@app.route("/tasks", methods=["POST"])
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
    if get_file_len(file) * 2 + db_methods.get_storage() > app.config['MAX_SYSTEM_STORAGE']:
        logger.critical('Storage overload has occured')
        return 'storage_overload'
    file_check_response = check_file(file, extension, ALLOWED_EXTENSIONS[file_ext_type], check_mime=True)
    if file_check_response != "ok":
        logger.info('Пользователь загрузил файл с ошибочным расширением: ' + file_check_response)
        return file_check_response

    if pdf_file:
        pdf_file_check_response = check_file(pdf_file, pdf_file.filename.rsplit('.', 1)[1], "pdf", check_mime=True)
        if pdf_file_check_response != "ok":
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
    file_id = db_methods.add_file_info_and_content(current_user.username, filepath, file_type, file_id)
    # use pdf from response or convert to pdf and save on disk and db
    if current_user.two_files and pdf_file:
        if get_file_len(pdf_file) * 2 + db_methods.get_storage() > app.config['MAX_SYSTEM_STORAGE']:
            logger.critical('Storage overload has occured')
            return 'storage_overload'
        logger.info(
            f"Запуск обработки файла {pdf_file.filename} пользователя {current_user.username} с критериями {current_user.criteria}")
        filenamepdf, extension = pdf_file.filename.rsplit('.', 1)
        filepathpdf = join(UPLOAD_FOLDER, f"{file_id}.{extension}")
        pdf_file.save(filepathpdf)
        converted_id = db_methods.add_file_to_db(filenamepdf, filepathpdf)
    else:
        converted_id = db_methods.write_pdf(filename, filepath)
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
    db_methods.add_check(file_id, check)  # add check for parsed_file to db
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    db_methods.add_celery_task(task.id, file_id)  # mapping celery_task to check (check_id = file_id)
    return {'task_id': task.id, 'check_id': str(file_id)}


@app.route("/recheck/<check_id>", methods=["GET"])
@login_required
def recheck(check_id):
    if not current_user.is_admin:
        abort(403)
    oid = ObjectId(check_id)
    check = db_methods.get_check(oid)

    if not check:
        abort(404)
    filepath = join(UPLOAD_FOLDER, f"{check_id}.{check.filename.rsplit('.', 1)[-1]}")
    check.is_ended = False
    db_methods.update_check(check)
    db_methods.write_file_from_db_file(oid, filepath)
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    db_methods.add_celery_task(task.id, check_id)  # mapping celery_task to check (check_id = file_id)
    return {'task_id': task.id, 'check_id': check_id}


@app.route("/tasks/<task_id>", methods=["GET"])
@login_required
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200


CRITERIA_LABELS = {'template_name': 'Соответствие названия файла шаблону',
                   'slides_number': 'Количество основных слайдов',
                   'slides_enum': 'Нумерация слайдов',
                   'slides_headers': 'Заголовки слайдов присутствуют и занимают не более двух строк',
                   'goals_slide': 'Слайд "Цель и задачи"', 'probe_slide': 'Слайд "Апробация работы"',
                   'actual_slide': 'Слайд с описанием актуальности работы', 'conclusion_slide': 'Слайд с заключением',
                   'slide_every_task': 'Наличие слайдов, посвященных задачам',
                   'pres_right_words': 'Проверка наличия определенных (правильных) слов в презентации',
                   'pres_image_share': 'Проверка доли объема презентации, приходящейся на изображения',
                   'pres_banned_words_check': 'Проверка наличия запретных слов в презентации',
                   'conclusion_actual': 'Соответствие заключения задачам',
                   'conclusion_along': 'Наличие направлений дальнейшего развития',
                   'simple_check': 'Простейшая проверка отчёта',
                   'banned_words_in_literature': 'Наличие запрещенных слов в списке литературы',
                   'banned_words_check': 'Проверка наличия запретных слов в тексте отчёта',
                   'page_counter': 'Проверка количества страниц',
                   'image_share_check': 'Проверка доли объема отчёта, приходящейся на изображения',
                   'right_words_check': 'Проверка наличия определенных (правильных) слов в тексте отчёта',
                   'first_pages_check': 'Проверка наличия обязательных страниц в отчете',
                   'main_character_check': 'Проверка фамилии и должности заведующего кафедрой',
                   'needed_headers_check': 'Проверка наличия обязательных заголовков в отчете',
                   'header_check': 'Проверка оформления заголовков отчета',
                   'literature_references': 'Проверка наличия ссылок на все источники',
                   'image_references': 'Проверка наличия ссылок на все рисунки',
                   'table_references': 'Проверка наличия ссылок на все таблицы',
                   'report_section_component': 'Проверка наличия необходимых компонент указанного раздела',
                   'main_text_check': 'Проверка оформления основного текста отчета'
                   }


@app.route("/results/<string:_id>", methods=["GET"])
def results(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return render_template("./404.html")
    check = db_methods.get_check(oid)
    if check is not None:
        # show processing time for user
        avg_process_time = None if check.is_ended else db_methods.get_average_processing_time()
        return render_template("./results.html", navi_upload=True, results=check,
                               columns=TABLE_COLUMNS, avg_process_time=avg_process_time,
                               stats=format_check(check.pack()))
    else:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return render_template("./404.html")


@app.route("/checks/<string:_id>", methods=["GET"])
@login_required
def checks(_id):
    try:
        f = db_methods.get_file_by_check(ObjectId(_id))
    except bson.errors.InvalidId:
        logger.error('_id exception in checks occured:', exc_info=True)
        return render_template("./404.html")
    if f is not None:
        n = 'txt/plain'
        if f.name.endswith('.ppt'):
            n = 'application/vnd.ms-powerpoint'
        elif f.name.endswith('.pptx'):
            n = 'application/vnd.openxmlformats-officedocument.presentationml.presentations'
        elif f.name.endswith('.odp'):
            n = 'application/vnd.oasis.opendocument.presentations'
        return Response(f.read(), mimetype=n)
    else:
        logger.info("Запрошенная презентация не найдена: " + _id)
        return render_template("./404.html")


################### Criterion packs ###################

@app.route("/criterion_pack", methods=["GET"])
@login_required
def criteria_pack_new():
    if not current_user.is_admin:
        abort(403)
    return render_template('./criteria_pack.html', name=current_user.name, navi_upload=True)


@app.route("/criterion_packs", methods=["GET"])
@login_required
def criteria_packs():
    if not current_user.is_admin:
        abort(403)
    packs = db_methods.get_criterion_pack_list()
    return render_template('./pack_list.html', packs=packs, name=current_user.name, navi_upload=True)


@app.route("/criterion_pack/<string:name>", methods=["GET"])
@login_required
def criteria_pack(name):
    if not current_user.is_admin:
        abort(403)

    pack = db_methods.get_criteria_pack(name)
    if not pack:
        abort(404)
    pack['raw_criterions'] = json.dumps(pack['raw_criterions'], indent=4, ensure_ascii=False)
    return render_template('./criteria_pack.html', pack=pack, name=current_user.name, navi_upload=True)


@app.route("/api/criterion_pack", methods=["POST"])
@login_required
def api_criteria_pack():
    if not current_user.is_admin:
        abort(403)
    form_data = dict(request.form)
    pack_name = form_data.get('pack_name')
    # get pack configuration info
    raw_criterions = form_data.get('raw_criterions')
    file_type = form_data.get('file_type')
    report_type = form_data.get('report_type')
    min_score = float(form_data.get('min_score', '1'))
    # weak validation
    try:
        raw_criterions = json.loads(raw_criterions)
    except:
        msg = f"Ошибка при парсинге критериев {raw_criterions} для набора {pack_name} от пользователя {current_user.name}"
        logger.info(msg)
        return msg, 400
    raw_criterions = raw_criterions if type(raw_criterions) is list else None
    file_type = file_type if file_type in BASE_PACKS.keys() else None
    min_score = min_score if min_score and (0 <= min_score <= 1) else None
    if not (raw_criterions and file_type and min_score):
        msg = f"Конфигурация набора критериев должна содержать список критериев (непустой список в формате JSON)," \
              f"тип файла (один из {list(BASE_PACKS.keys())})," \
              f"пороговый балл (0<=x<=1). Получено: {form_data}, после обработки: file_type - {file_type}," \
              f"min_score - {min_score}, raw_criterions - {raw_criterions}"
        return {'data': msg, 'time': datetime.now()}, 400
    #  testing pack initialization
    file_type_info = {'type': file_type}
    if file_type == DEFAULT_REPORT_TYPE_INFO['type']:
        file_type_info['report_type'] = report_type if report_type in REPORT_TYPES else DEFAULT_REPORT_TYPE_INFO[
            'report_type']
    inited, err = init_criterions(raw_criterions, file_type=file_type_info)
    if len(raw_criterions) != len(inited) or err:
        msg = f"При инициализации набора {pack_name} возникли ошибки. JSON-конфигурация: '{raw_criterions}'. Успешно инициализированные: {inited}. Возникшие ошибки: {err}."
        return {'data': msg, 'time': datetime.now()}, 400
    # if ok - save to DB
    db_methods.save_criteria_pack({
        'name': pack_name,
        'raw_criterions': raw_criterions,
        'file_type': file_type_info,
        'min_score': min_score
    })
    return {'data': f"Набор '{pack_name}' сохранен", 'time': datetime.now()}, 200


################### ###################

@app.route("/get_last_check_results/<string:moodle_id>", methods=["GET"])
@login_required
def get_latest_user_check(moodle_id):
    check = db_methods.get_latest_user_check_by_moodle(moodle_id)
    logger.error(str(check))
    if check:
        check = check[0]
        return redirect(url_for('results', _id=str(check['_id'])))
    else:
        return render_template("./404.html")


@app.route("/get_pdf/<string:_id>", methods=["GET"])
@login_required
def get_pdf(_id):
    try:
        file = db_methods.find_pdf_by_file_id(ObjectId(_id))
    except bson.errors.InvalidId:
        logger.error('_id exception in fetching pdf occured:', exc_info=True)
        return render_template("./404.html")
    if file is not None:
        return Response(file.read(), mimetype='application/pdf')
    else:
        logger.info(f'pdf файл для проверки {id} не найден')
        return render_template("./404.html")


@app.route("/check_list")
@login_required
def check_list():
    return render_template("./check_list.html", name=current_user.name, navi_upload=True)



@app.route("/check_list/data")
@login_required
def check_list_data():
    data = request.args.copy()
    filter_query = checklist_filter(data)
    # parse and validate rest query
    limit = data.get("limit", '')
    limit = int(limit) if limit.isdigit() else 10

    offset = data.get("offset", '')
    offset = int(offset) if offset.isdigit() else 0

    sort = data.get("sort")
    sort = 'upload-date' if not sort else sort

    order = data.get("order")
    order = 'desc' if not order else order

    sort = "_id" if sort == "upload-date" else sort

    query = dict(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    if data.get("latest"):
        rows, count = db_methods.get_latest_check_cursor(**query)
    else:
        # get data and records count
        rows, count = db_methods.get_checks_cursor(**query)

    # construct response
    response = {
        "total": count,
        "rows": [format_check_for_table(item) for item in rows]
    }

    # return json data
    return jsonify(response)


def get_query(req):
    # query for download csv/zip
    filter_query = checklist_filter(req.args)
    limit = False
    offset = False
    sort = req.args.get("sort", "")
    sort = 'upload-date' if not sort else sort
    order = req.args.get("order", "")
    order = 'desc' if not order else order
    sort = "_id" if sort == "upload-date" else sort
    latest = True if req.args.get("latest") else False
    return dict(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order, latest=latest)


def get_stats():
    rows, count = db_methods.get_checks(**get_query(request))
    return [format_check_for_table(item, set_link=URL_DOMEN) for item in rows]


@app.route("/get_csv")
@login_required
def get_csv():
    from io import StringIO
    if not current_user.is_admin:
        abort(403)
    response = get_stats()
    df = pd.read_json(StringIO(json.dumps(response)))
    return Response(
        df.to_csv(sep=',', encoding='utf-8', decimal=','),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment"}
    )


@app.route("/get_zip")
@login_required
def get_zip():
    if not current_user.is_admin:
        abort(403)

    # create tmp folder
    dirpath = tempfile.TemporaryDirectory()

    # write files
    checks_list, _ = db_methods.get_checks(**get_query(request))
    for check in checks_list:
        db_file = db_methods.find_pdf_by_file_id(check['_id'])
        if db_file is not None:
            with open(f"{dirpath.name}/{db_file.filename}", 'wb') as os_file:
                os_file.write(db_file.read())

    # add csv
    response = get_stats()
    df = pd.read_json(StringIO(json.dumps(response)))
    df.to_csv(f"{dirpath.name}/Статистика.csv")

    # zip
    tmp = tempfile.TemporaryDirectory()
    archive_path = shutil.make_archive(f"{tmp}/archive", 'zip', dirpath.name)
    dirpath.cleanup()

    # send
    with open(archive_path, 'rb') as zip_file:
        return Response(
            zip_file.read(),
            mimetype="application/zip",
            headers={"Content-disposition": "attachment"}
        )


@app.route("/logs")
@login_required
def logs():
    return render_template("./logs.html", name=current_user.name, navi_upload=True)


@app.route("/logs/data")
@login_required
def logs_data():
    filters = request.args.get("filter", "{}")
    try:
        filters = json.loads(filters)
        filters = filters if filters else {}
    except Exception as e:
        logger.warning("Can't parse filters")
        logger.warning(repr(e))
        filters = {}

    # req filter to mongo query filter conversion
    filter_query = {}
    if f_service_name := filters.get("service-name", None):
        filter_query["serviceName"] = {"$regex": f_service_name}

    if f_levelname := filters.get("levelname", None):
        filter_query["levelname"] = {"$regex": f_levelname}

    if f_pathname := filters.get("pathname", None):
        filter_query["pathname"] = {"$regex": f_pathname}

    f_lineno = filters.get("lineno", "")
    f_lineno_list = list(filter(lambda val: val, f_lineno.split("-")))
    try:
        if len(f_lineno_list) == 1:
            filter_query["lineno"] = int(f_lineno_list[0])
        elif len(f_lineno_list) > 1:
            filter_query["lineno"] = {
                "$gte": int(f_lineno_list[0]),
                "$lte": int(f_lineno_list[1])
            }
    except Exception as e:
        logger.warning("Can't apply lineno filter")
        logger.warning(repr(e))

    f_timestamp = filters.get("timestamp", "")
    f_timestamp_list = list(filter(lambda val: val, f_timestamp.split("-")))
    try:
        if len(f_timestamp_list) == 1:
            date = datetime.strptime(f_timestamp_list[0], "%d.%m.%Y")
            filter_query['timestamp'] = {
                "$gte": date,
                "$lte": date + timedelta(hours=23, minutes=59, seconds=59)
            }
        elif len(f_timestamp_list) > 1:
            filter_query['timestamp'] = {
                "$gte": datetime.strptime(f_timestamp_list[0], "%d.%m.%Y"),
                "$lte": datetime.strptime(f_timestamp_list[1], "%d.%m.%Y")
            }
    except Exception as e:
        logger.warning("Can't apply timestamp filter")
        logger.warning(repr(e))

    # parse and validate rest query
    limit = request.args.get("limit", "")
    limit = int(limit) if limit.isnumeric() else 10

    offset = request.args.get("offset", "")
    offset = int(offset) if offset.isnumeric() else 0

    sort = request.args.get("sort", "")
    sort = 'timestamp' if not sort else sort

    order = request.args.get("order", "")
    order = 'desc' if not order else order

    # get data and records count
    rows, count = db_methods.get_logs_cursor(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    # construct response
    response = {
        "total": count,
        "rows": [{
            "timestamp": item["timestamp"].strftime("%d.%m.%Y %H:%M:%S"),
            "service-name": item["serviceName"],
            "levelname": item["levelname"],
            "message": item["message"],
            "pathname": item["pathname"],
            "lineno": item["lineno"]
        } for item in rows]
    }

    # return json data
    return jsonify(response)


@app.route("/version")
def version():
    return render_template("./version.html")


@app.route('/profile', methods=["GET"], defaults={'username': ''})
@app.route('/profile/<string:username>', methods=["GET"])
@login_required
def profile(username):
    return abort(404)
    # if current_user.is_admin:
    #     if username == '':
    #         return redirect(url_for("profile", username=current_user.username))
    #     u = db_methods.get_user(username)
    #     me = True if username == current_user.username else False
    #     if u is not None:
    #         return render_template("./profile.html", navi_upload=True, name=current_user.name, user=u, me=me)
    #     else:
    #         logger.info("Запрошенный пользователь не найден: " + username)
    #         return render_template("./404.html")
    # else:
    #     abort(403)


@app.route("/capacity", methods=["GET"])
def system_capacity():
    units = {'b': 1, 'mb': 1024 ** 2, 'gb': 1024 ** 3}
    unit = units.get(request.args.get('unit', 'gb').lower(), units['gb'])
    current_size = db_methods.get_storage()
    ratio = current_size / app.config['MAX_SYSTEM_STORAGE']
    return {
        'size': current_size / unit,
        'max_size': app.config['MAX_SYSTEM_STORAGE'] / unit,
        'ratio': ratio
    }


# Handle exceptions

@app.errorhandler(413)
def request_entity_too_large(error=None):
    return 'File exceeded the upload limit', 413


# Redirection:

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login"))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    logger.info("Страница /" + path + " не найдена!")
    return render_template("./404.html")


@app.route("/")
def default():
    return redirect(url_for("upload"))


# Disable caching:

@app.after_request
def add_header(r):
    if DEBUG:
        r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        r.headers["Pragma"] = "no-cache"
        r.headers["Expires"] = "0"
        r.headers['Cache-Control'] = 'public, max-age=0'
    return r


class ReverseProxied(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        forwarded_scheme = environ.get("HTTP_X_FORWARDED_PROTO", None)
        preferred_scheme = app.config.get("PREFERRED_URL_SCHEME", None)
        if "https" in [forwarded_scheme, preferred_scheme]:
            environ["wsgi.url_scheme"] = "https"
        return self.app(environ, start_response)


if __name__ == '__main__':
    DEBUG = True
    if len(argv) == 2:
        if argv[1] == '-p':
            DEBUG = False
    else:
        logger.info("Приложение принимает только один аргумент")
        logger.info("Используйте \"-d\" для запуска в отладочном режиме и \"-p\" для запуска в рабочем режиме")
        logger.info("По умолчанию выбран отладочный режим...")

    if pre_luncher.init(app, DEBUG):
        app.wsgi_app = ReverseProxied(app.wsgi_app)
        port = 8080
        ip = '0.0.0.0'
        logger.info("Сервер запущен по адресу http://" + str(ip) + ':' + str(port) + " в " +
                    ("отладочном" if DEBUG else "рабочем") + " режиме")
        utils.create_consumers(app.config['LTI_CONSUMERS'])
        app.run(debug=DEBUG, host=ip, port=8080, use_reloader=True)
