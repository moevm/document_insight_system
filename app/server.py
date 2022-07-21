import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
from os.path import join
from sys import argv

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
from db import db_methods
from db.db_types import Check
from lti_session_passback.lti import utils
from lti_session_passback.lti.check_request import check_request
from main.check_packs import BASE_PACKS
from root_logger import get_logging_stdout_handler, get_root_logger
from servants import pre_luncher
from tasks import create_task
from utils import checklist_filter, decorator_assertion, get_file_len, timezone_offset, format_check

logger = get_root_logger('web')
UPLOAD_FOLDER = '/usr/src/project/files'
ALLOWED_EXTENSIONS = {
    'pres': {'ppt', 'pptx', 'odp'},
    'report': {'doc', 'odt', 'docx'}
}
DOCUMENT_TYPES = {'Лабораторная работа', 'Курсовая работа', 'ВКР'}
TABLE_COLUMNS = ['Solution', 'User', 'File', 'Check added', 'LMS date', 'Score']

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
        # - file type (pres or report)
        file_type = custom_params.get('file_type') & set(BASE_PACKS.keys())  # check that file_type is allowed
        file_type = file_type if file_type else 'pres'  # 'pres' file_type as default
        # - file formats
        formats = sorted((set(map(str.lower, custom_params.get('formats', '').split(','))) & ALLOWED_EXTENSIONS[
            file_type] or ALLOWED_EXTENSIONS[file_type]))
        custom_criterion_pack = custom_params.get('pack', BASE_PACKS.get(file_type))

        role = utils.get_role(temporary_user_params)

        logout_user()

        lti_user = db_methods.add_user(user_id, is_LTI=True)
        if lti_user:
            lti_user.name = person_name
            lti_user.is_admin = role
        else:
            lti_user = db_methods.get_user(user_id)
        lti_user.formats = formats
        lti_user.params_for_passback = params_for_passback
        lti_user.lms_user_id = lms_user_id
        db_methods.edit_user(lti_user)

        login_user(lti_user)
        lti_user.update_criteria(custom_criterion_pack)
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
    elif request.method == "DELETE":
        return user.signout()


# Main chapters req handlers:

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if current_user.is_LTI or True:  # app.recaptcha.verify():
            return run_task()
        else:
            abort(401)
    elif request.method == "GET":
        formats = set(current_user.formats)
        file_type = current_user.file_type
        formats = formats & ALLOWED_EXTENSIONS[file_type] if formats else ALLOWED_EXTENSIONS[file_type]
        return render_template("./upload.html", navi_upload=False, name=current_user.name, file_type=file_type,
                               formats=sorted(formats))


@app.route("/tasks", methods=["POST"])
@login_required
def run_task():
    file = request.files.get("file")
    file_type = request.form.get('file_type', 'pres')
    if not file:
        logger.critical("request doesn't include file")
        return "request doesn't include file"
    if get_file_len(file) * 2 + db_methods.get_storage() > app.config['MAX_SYSTEM_STORAGE']:
        logger.critical('Storage overload has occured')
        return 'storage_overload'
    logger.info(
        f"Запуск обработки файла {file.filename} пользователя {current_user.username} с критериями {current_user.criteria}")

    file_id = ObjectId()
    # save to file on disk for future checking
    filename, extension = file.filename.rsplit('.', 1)
    filepath = join(UPLOAD_FOLDER, f"{file_id}.{extension}")
    file.save(filepath)
    # add file and file's info to db
    file_id = db_methods.add_file_info_and_content(current_user.username, filepath, file_type, file_id)
    # convert to pdf and save on disk and db
    converted_id = db_methods.write_pdf(filename, filepath)  # convert to pdf for preview
    # TODO: validate that enabled_checks match file_type
    check = Check({
        '_id': file_id,
        'conv_pdf_fs_id': converted_id,
        'user': current_user.username,
        'lms_user_id': current_user.lms_user_id,
        'enabled_checks': current_user.criteria,
        'file_type': current_user.file_type,
        'filename': file.filename,
        'score': -1,  # score=-1 -> checking in progress
        'is_ended': False,
        'is_failed': False
    })
    db_methods.add_check(file_id, check)  # add check for parsed_file to db
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    db_methods.add_celery_task(task.id, file_id)  # mapping celery_task to check (check_id = file_id)
    return {'task_id': task.id, 'check_id': str(file_id)}


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
                   'conclusion_actual': 'Соответствие заключения задачам',
                   'conclusion_along': 'Наличие направлений дальнейшего развития',
                   'simple_check': 'Простейшая проверка отчёта',
                   'banned_words_in_literature': 'Наличие запрещенных слов в списке литературы',
                   'banned_words_check': 'Проверка наличия запретных слов в тексте отчёта',
                   'page_counter': 'Проверка количества страниц',
                   'image_share_check': 'Проверка доли объема отчёта, приходящейся на изображения',
                   'right_words_check': 'Проверка наличия определенных (правильных) слов в тексте отчёта'
}


@app.route("/results/<string:_id>", methods=["GET"])
@login_required
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
        return render_template("./results.html", navi_upload=True, name=current_user.name, results=check, id=_id,
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


@app.route("/criteria", methods=["GET", "POST"])
@login_required
def criteria():
    if current_user.is_admin:
        if request.method == "GET":
            return render_template("./criteria.html", navi_upload=True, name=current_user.name,
                                   crit=current_user.criteria)
        elif request.method == "POST":
            return user.update_criteria(request.json)
    else:
        abort(403)


@app.route("/check_list")
@login_required
def check_list():
    return render_template("./check_list.html", name=current_user.name, navi_upload=True)


@app.route("/check_list/data")
@login_required
def check_list_data():
    filter_query = checklist_filter(request)
    # parse and validate rest query
    limit = request.args.get("limit", "")
    limit = int(limit) if limit.isnumeric() else 10

    offset = request.args.get("offset", "")
    offset = int(offset) if offset.isnumeric() else 0

    sort = request.args.get("sort", "")
    sort = 'upload-date' if not sort else sort

    order = request.args.get("order", "")
    order = 'desc' if not order else order

    sort = "_id" if sort == "upload-date" else sort

    query = dict(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    if request.args.get("latest"):
        rows, count = db_methods.get_latest_check_cursor(**query)
    else:
        # get data and records count
        rows, count = db_methods.get_checks_cursor(**query)

    # construct response
    response = {
        "total": count,
        "rows": [{
            "_id": str(item["_id"]),
            "filename": item["filename"],
            "user": item["user"],
            "lms-user-id": item["lms_user_id"] if item.get("lms_user_id") else '-',
            "upload-date": (item["_id"].generation_time + timezone_offset).strftime("%d.%m.%Y %H:%M:%S"),
            "moodle-date": item['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S") if item.get(
                'lms_passback_time') else '-',
            "score": item["score"]
        } for item in rows]
    }

    # return json data
    return jsonify(response)


def get_query(req):
    # query for download csv/zip
    filter_query = checklist_filter(req)
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
    return [{
        "_id": str(item["_id"]),
        "filename": item["filename"],
        "user": item["user"],
        "lms-username": item["user"].rsplit('_', 1)[0],
        "lms-user-id": item["lms_user_id"] if item.get("lms_user_id") else '-',
        "upload-date": (item["_id"].generation_time + timezone_offset).strftime("%d.%m.%Y %H:%M:%S"),
        "moodle-date": item['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S") if item.get(
            'lms_passback_time') else '-',
        "score": item["score"]
    } for item in rows]


@app.route("/get_csv")
@login_required
def get_csv():
    if not current_user.is_admin:
        abort(403)
    response = get_stats()
    df = pd.read_json(json.dumps(response))
    return Response(
        df.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment"})


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
    df = pd.read_json(json.dumps(response))
    df.to_csv(f"{dirpath.name}/Презентации.csv")

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
    if current_user.is_admin:
        if username == '':
            return redirect(url_for("profile", username=current_user.username))
        u = db_methods.get_user(username)
        me = True if username == current_user.username else False
        if u is not None:
            return render_template("./profile.html", navi_upload=True, name=current_user.name, user=u, me=me)
        else:
            logger.info("Запрошенный пользователь не найден: " + username)
            return render_template("./404.html")
    else:
        abort(403)


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
        port = 8080
        ip = '0.0.0.0'
        logger.info("Сервер запущен по адресу http://" + str(ip) + ':' + str(port) + " в " +
                    ("отладочном" if DEBUG else "рабочем") + " режиме")
        utils.create_consumers(app.config['LTI_CONSUMERS'])
        app.run(debug=DEBUG, host=ip, port=8080, use_reloader=True)
