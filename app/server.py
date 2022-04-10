import json
import os
import shutil
import tempfile
from datetime import datetime, timedelta
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

import app.servants.user as user
from app.bd_helper import bd_helper
from app.lti_session_passback.lti.check_request import check_request
from app.root_logger import get_logging_stdout_handler, get_root_logger
from app.servants import data as data
from app.servants import pre_luncher
from app.servants.user import update_criteria
from app.utils.checklist_filter import checklist_filter
from app.utils.decorators import decorator_assertion
from app.utils.get_file_len import get_file_len
from lti_session_passback.lti import utils

logger = get_root_logger('web')
UPLOAD_FOLDER = './files'
ALLOWED_EXTENSIONS = set(('ppt', 'pptx', 'odp'))
columns = ['Solution', 'User', 'File', 'Check added', 'LMS date', 'Score']

app = Flask(__name__, static_folder="./../src/", template_folder="./../templates/")
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
    return bd_helper.get_user(user_id)


# User pages request handlers:
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
        formats = sorted((set(map(str.lower, custom_params.get('formats', '').split(','))) & ALLOWED_EXTENSIONS or ALLOWED_EXTENSIONS))
        custom_criteria = utils.get_criteria_from_launch(temporary_user_params)
        role = utils.get_role(temporary_user_params)

        logout_user()

        user = bd_helper.add_user(user_id, is_LTI = True)
        if user:
            user.name = person_name
            user.is_admin = role
        else:
            user = bd_helper.get_user(user_id)
        user.formats = formats
        user.params_for_passback = params_for_passback
        user.lms_user_id = lms_user_id
        bd_helper.edit_user(user)

        login_user(user)
        update_criteria(custom_criteria)
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


# Main pages request handlers:

@app.route("/upload", methods=["GET", "POST", "PUT"])
@login_required
def upload():
    if request.method == "POST":
        if current_user.is_LTI or app.recaptcha.verify() :
            return data.upload(request, UPLOAD_FOLDER)
        else:
            abort(401)
    elif request.method == "GET":
        return render_template("./upload.html", debug=DEBUG, navi_upload=False, name=current_user.name, formats=current_user.formats or ALLOWED_EXTENSIONS)
    elif request.method == "PUT":
        return data.remove_presentation(request.json)


@app.route("/tasks", methods=["POST"])
@login_required
def run_task():
    file = request.files["presentation"]
    if get_file_len(file)*2 + bd_helper.get_storage() > app.config['MAX_SYSTEM_STORAGE']:
        logger.critical('Storage overload has occured')
        return 'storage_overload'
    try:
        converted_id = bd_helper.write_pdf(file)
    except TypeError:
        return 'Not OK, pdf converter refuses connection. Try reloading.'

    filename = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filename)

    from app.tasks import create_task  # ##
    task = create_task.delay(filename, str(converted_id), username=current_user.username)
    return jsonify({"task_id": task.id}), 202


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


CRITERIA_LABELS = {'template_name': 'Соответствие названия файла шаблону', 'slides_number': 'Количество основных слайдов',
                    'slides_enum': 'Нумерация слайдов', 'slides_headers': 'Заголовки слайдов присутствуют и занимают не более двух строк', 'goals_slide': 'Слайд "Цель и задачи"', 'probe_slide': 'Слайд "Апробация работы"',
                    'actual_slide': 'Слайд с описанием актуальности работы', 'conclusion_slide': 'Слайд с заключением', 'slide_every_task': 'Наличие слайдов, посвященных задачам',
                    'conclusion_actual': 'Соответствие заключения задачам', 'conclusion_along': 'Наличие направлений дальнейшего развития'}


@app.route("/results/<string:_id>", methods=["GET"])
@login_required
def results(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return render_template("./404.html")
    check = bd_helper.get_check(oid)
    if check is not None:
        return render_template("./results.html", navi_upload=True, name=current_user.name, results=check, id=_id, fi=check.filename,
                                columns=columns, stats = bd_helper.format_check(check.pack()), labels=CRITERIA_LABELS)
    else:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return render_template("./404.html")


@app.route("/checks/<string:_id>", methods=["GET"])
@login_required
def checks(_id):
    try:
        f = bd_helper.get_presentation_check(ObjectId(_id))
    except bson.errors.InvalidId:
        logger.error('_id exception in checks occured:', exc_info=True)
        return render_template("./404.html")
    if f is not None:
        n = 'txt/plain'
        if f.name.endswith('.ppt'):
            n = 'application/vnd.ms-powerpoint'
        elif f.name.endswith('.pptx'):
            n = 'application/vnd.openxmlformats-officedocument.presentationml.presentation'
        elif f.name.endswith('.odp'):
            n = 'application/vnd.oasis.opendocument.presentation'
        return Response(f.read(), mimetype=n)
    else:
        logger.info("Запрошенная презентация не найдена: " + _id)
        return render_template("./404.html")


@app.route("/get_last_check_results/<string:moodle_id>", methods=["GET"])
@login_required
def get_latest_user_check(moodle_id):
    check = bd_helper.get_latest_user_check_by_moodle(moodle_id)
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
        file = bd_helper.find_pdf_by_file_id(ObjectId(_id))
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
            return render_template("./criteria.html", navi_upload=True, name=current_user.name, crit=current_user.criteria)
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
        rows, count = bd_helper.get_latest_check_cursor(**query)
    else:
        # get data and records count
        rows, count = bd_helper.get_checks_cursor(**query)

    # construct response
    response = {
        "total": count,
        "rows": [{
            "_id": str(item["_id"]),
            "filename": item["filename"],
            "user": item["user"],
            "lms-user-id": item["lms_user_id"] if item.get("lms_user_id") else '-',
            "upload-date": item["_id"].generation_time.strftime("%d.%m.%Y %H:%M:%S"),
            "moodle-date": item['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S") if item.get('lms_passback_time') else '-',
            "score": item["score"]
        } for item in rows]
    }

    # return json data
    return jsonify(response)


def get_query(request):
    # query for download csv/zip
    filter_query = checklist_filter(request)
    limit = False
    offset = False
    sort = request.args.get("sort", "")
    sort = 'upload-date' if not sort else sort
    order = request.args.get("order", "")
    order = 'desc' if not order else order
    sort = "_id" if sort == "upload-date" else sort
    return dict(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)


@app.route("/get_csv")
@login_required
def get_csv():
    rows, count = bd_helper.get_checks_cursor(**get_query(request))
    response = [{
            "_id": str(item["_id"]),
            "filename": item["filename"],
            "user": item["user"],
            "lms-username": item["user"].rsplit('_', 1)[0],
            "lms-user-id": item["lms_user_id"] if item.get("lms_user_id") else '-',
            "upload-date": item["_id"].generation_time.strftime("%d.%m.%Y %H:%M:%S"),
            "moodle-date": item['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S") if item.get('lms_passback_time') else '-',
            "score": item["score"]
        } for item in rows]

    df = pd.read_json(json.dumps(response))
    return Response(
        df.to_csv(),
        mimetype="text/csv",
        headers={"Content-disposition": "attachment"})


@app.route("/get_zip")
@login_required
def get_zip():
    # create tmp folder
    dirpath = tempfile.TemporaryDirectory()

    # write files
    checks, _ = bd_helper.get_checks_cursor(**get_query(request))
    for check in checks:
        db_file = bd_helper.find_pdf_by_file_id(check['_id'])
        if db_file is not None:
            with open(f"{dirpath.name}/{db_file.filename}", 'wb') as os_file:
                os_file.write(db_file.read())
    
    # zip
    archive_path = shutil.make_archive('archive', 'zip', dirpath.name)
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

    # request filter to mongo query filter conversion
    filter_query = {}
    if f_service_name := filters.get("service-name", None):
        filter_query["serviceName"] = { "$regex": f_service_name }

    if f_levelname := filters.get("levelname", None):
        filter_query["levelname"] = { "$regex": f_levelname }

    if f_pathname := filters.get("pathname", None):
        filter_query["pathname"] = { "$regex": f_pathname }

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
    rows, count = bd_helper.get_logs_cursor(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

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
        u = bd_helper.get_user(username)
        me = True if username == current_user.username else False
        if u is not None:
            return render_template("./profile.html", navi_upload=True, name=current_user.name, user=u, me=me)
        else:
            logger.info("Запрошенный пользователь не найден: " + username)
            return render_template("./404.html")
    else:
        abort(403)


# Handle exceptions

@app.errorhandler(413)
def request_entity_too_large(error):
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
    if len(argv) == 2:
        if argv[1] == '-d':
            DEBUG = True
        elif argv[1] == '-p':
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
        app.run(debug=DEBUG, host=ip, port=8080, use_reloader=False)
