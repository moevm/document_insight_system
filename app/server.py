from datetime import datetime, timedelta
import logging
from sys import argv

import json
import bson
import pymongo
from bson import ObjectId
from flask import Flask, request, redirect, url_for, render_template, Response, abort, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user

from celery.result import AsyncResult
from celery import Celery
from app.tasks import create_task
import os

import app.servants.user as user
from app.servants import data as data
from app.bd_helper import bd_helper
from app.servants import pre_luncher
from app.servants.user import update_criteria

from app.utils.decorators import decorator_assertion
from app.utils.get_file_len import get_file_len
from app.lti_session_passback.lti.check_request import check_request
from lti_session_passback.lti import utils

from flask_recaptcha import ReCaptcha

from logging import getLogger
logger = getLogger('root')
logger.setLevel(logging.DEBUG)

DEBUG = True

ALLOWED_EXTENSIONS = {'pptx', 'odp', 'ppt'}
UPLOAD_FOLDER = './files'
columns = ['Solution', 'User', 'File', 'Check added', 'LMS date', 'Score']

app = Flask(__name__, static_folder="./../src/", template_folder="./../templates/")
app.config.from_pyfile('settings.py')
app.recaptcha = ReCaptcha(app=app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379'
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379'
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
        params_for_passback = utils.extract_passback_params(temporary_user_params)
        custom_params = utils.get_custom_params(temporary_user_params)
        custom_criteria = utils.get_criteria_from_launch(temporary_user_params)
        role = utils.get_role(temporary_user_params)

        logout_user()

        user = bd_helper.add_user(user_id, is_LTI = True)
        if user:
            user.name = person_name
            user.is_admin = role
        else:
            user = bd_helper.get_user(user_id)

        user.params_for_passback = params_for_passback
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
        return render_template("./upload.html", debug=DEBUG, navi_upload=False, name=current_user.name)
    elif request.method == "PUT":
        return data.remove_presentation(request.json)


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
                                columns=columns, stats = bd_helper.format_check(check.pack()))
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


@app.route("/check_info/<string:_id>", methods=["GET"])
@login_required
def get_check_info(_id):
    try:
        check_info = bd_helper.get_check(ObjectId(_id))
        if check_info:
            info = ['score', 'status']
            return jsonify({item: getattr(check_info, item, None) for item in info})
        else:
            return jsonify({'not_found': f"Check with id={_id} doesn't exist"})
    except bson.errors.InvalidId:
        return jsonify({'error': '_id exception has occured'})


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
    # transform json filter into dict
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
    if f_filename := filters.get("filename", None):
        filter_query["filename"] = { "$regex": f_filename }

    if f_user := filters.get("user", None):
        filter_query["user"] = { "$regex": f_user }

    f_upload_date = filters.get("upload-date", "")
    f_upload_date_list = list(filter(lambda val: val, f_upload_date.split("-")))
    try:
        if len(f_upload_date_list) == 1:
            date = datetime.strptime(f_upload_date_list[0], "%d.%m.%Y")
            filter_query["_id"] = {
                "$gte": ObjectId.from_datetime(date),
                "$lte": ObjectId.from_datetime(date + timedelta(hours=23, minutes=59, seconds=59))
            }
        elif len(f_upload_date_list) > 1:
            filter_query["_id"] = {
                "$gte": ObjectId.from_datetime(datetime.strptime(f_upload_date_list[0], "%d.%m.%Y")),
                "$lte": ObjectId.from_datetime(datetime.strptime(f_upload_date_list[1], "%d.%m.%Y"))
            }
    except Exception as e:
        logger.warning("Can't apply upload-date filter")
        logger.warning(repr(e))

    f_moodle_date = filters.get("moodle-date", "")
    f_moodle_date_list = list(filter(lambda val: val, f_moodle_date.split("-")))
    try:
        if len(f_moodle_date_list) == 1:
            date = datetime.strptime(f_moodle_date_list[0], "%d.%m.%Y")
            filter_query['lms_passback_time'] = {
                "$gte": date,
                "$lte": date + timedelta(hours=23, minutes=59, seconds=59)
            }
        elif len(f_moodle_date_list) > 1:
            filter_query['lms_passback_time'] = {
                "$gte": datetime.strptime(f_moodle_date_list[0], "%d.%m.%Y"),
                "$lte": datetime.strptime(f_moodle_date_list[1], "%d.%m.%Y")
            }
    except Exception as e:
        logger.warning("Can't apply moodle-date filter")
        logger.warning(repr(e))

    f_score = filters.get("score", "")
    f_score_list = list(filter(lambda val: val, f_score.split("-")))
    try:
        if len(f_score_list) == 1:
            filter_query["score"] = float(f_score_list[0])
        elif len(f_score_list) > 1:
            filter_query["score"] = {
                "$gte": float(f_score_list[0]),
                "$lte": float(f_score_list[1])
            }
    except Exception as e:
        logger.warning("Can't apply score filter")
        logger.warning(repr(e))

    # set user filter for current non-admin user
    if not current_user.is_admin:
        filter_query["user"] = current_user.username

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

    # get data and records count
    rows, count = bd_helper.get_checks_cursor(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    # construct response
    response = {
        "total": count,
        "rows": [{
            "_id": str(item["_id"]),
            "filename": item["filename"],
            "user": item["user"],
            "upload-date": item["_id"].generation_time.strftime("%d.%m.%Y %H:%M:%S"),
            "moodle-date": item['lms_passback_time'].strftime("%d.%m.%Y %H:%M:%S") if item.get('lms_passback_time') else '-',
            "score": item["score"]
        } for item in rows]
    }

    # return json data
    return jsonify(response)


@app.route("/version")
def version():
    return render_template("./version.html")


@app.route("/tasks", methods=["POST"])
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

    from app.tasks import create_task  ###
    task = create_task.delay(filename, str(converted_id))
    return jsonify({"task_id": task.id}), 202


@app.route("/tasks/<task_id>", methods=["GET"])
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result
    }
    return jsonify(result), 200

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
