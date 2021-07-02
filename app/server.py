from datetime import datetime
import logging
from sys import argv

import json
import bson
import pymongo
from bson import ObjectId
from flask import Flask, request, redirect, url_for, render_template, Response, abort, jsonify
from flask_login import LoginManager, login_user, current_user, login_required


import app.servants.user as user
from app.servants import data as data
from app.bd_helper.bd_helper import (
    get_user, get_check, get_presentation_check, users_collection,
    get_all_checks, get_user_checks, format_stats, format_check, get_checks_cursor)
from app.servants import pre_luncher

from app.utils.decorators import decorator_assertion

from flask_recaptcha import ReCaptcha

from logging import getLogger
logger = getLogger('root')
logger.setLevel(logging.DEBUG)

DEBUG = True

ALLOWED_EXTENSIONS = {'pptx', 'odp', 'ppt'}
UPLOAD_FOLDER = './files'
columns = ['Solution', 'User', 'File', 'Check added', 'Score']

app = Flask(__name__, static_folder="./../src/", template_folder="./../templates/")
app.config.from_pyfile('settings.py')
app.recaptcha = ReCaptcha(app=app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_pyfile('settings.py')

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)

log = logging.getLogger('werkzeug')
log.setLevel(logging.DEBUG)


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


# User pages request handlers:

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
        if app.recaptcha.verify():
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
    check = get_check(oid)
    if check is not None:
        return render_template("./results.html", navi_upload=True, name=current_user.name, results=check, id=_id, fi=check.filename,
                                columns=columns, stats = format_check(check.pack()))
    else:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return render_template("./404.html")


@app.route("/checks/<string:_id>", methods=["GET"])
@login_required
def checks(_id):
    try:
        f = get_presentation_check(ObjectId(_id))
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


@app.route("/criteria", methods=["GET", "POST"])
@login_required
def criteria():
    if request.method == "GET":
        return render_template("./criteria.html", navi_upload=True, name=current_user.name, crit=current_user.criteria)
    elif request.method == "POST":
        return user.update_criteria(request.json)

@app.route("/stats", methods=["GET"])
@login_required
def stats():
    if current_user.is_admin:
        stats = format_stats(get_all_checks())
        return render_template("./stats.html", name=current_user.name, columns = columns, stats = stats)
    else:
         login = current_user.username
         user = users_collection.find_one({'username': login})
         stats = format_stats(get_user_checks(login))
         return render_template("./stats.html", name=current_user.name, columns = columns, stats = stats)


@app.route("/check_list")
@login_required
def check_list():
    return render_template("./check_list.html", name=current_user.name)


@app.route("/check_list/data")
@login_required
def check_list_data():
    # transform json filter into dict
    filters = request.args.get("filter", "")
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
            filter_query["_id"] = ObjectId.from_datetime(datetime.strptime(f_upload_date_list[0], "%d.%m.%Y"))
        elif len(f_upload_date_list) > 1:
            filter_query["_id"] = {
                "$gte": ObjectId.from_datetime(datetime.strptime(f_upload_date_list[0], "%d.%m.%Y")),
                "$lte": ObjectId.from_datetime(datetime.strptime(f_upload_date_list[1], "%d.%m.%Y"))
            }
    except Exception as e:
        logger.warning("Can't apply upload-date filter")
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
    order = request.args.get("order", "")

    # get data and records count
    rows, count = get_checks_cursor(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    # construct response
    response = {
        "total": count,
        "rows": [{
            "_id": str(item["_id"]),
            "filename": item["filename"],
            "user": item["user"],
            "upload-date": item["_id"].generation_time.strftime("%d.%m.%Y %H:%M:%S"),
            "score": item["score"]
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
    if username == '':
        return redirect(url_for("profile", username=current_user.username))
    u = get_user(username)
    me = True if username == current_user.username else False
    if u is not None:
        return render_template("./profile.html", navi_upload=True, name=current_user.name, user=u, me=me)
    else:
        logger.info("Запрошенный пользователь не найден: " + username)
        return render_template("./404.html")


@app.route("/presentations", methods=["GET"], defaults={'username': ''})
@app.route('/presentations/<string:username>', methods=["GET"])
@login_required
def presentations(username):
    if username == '':
        return redirect(url_for("presentations", username=current_user.username))
    u = user.get_rich(username)
    me = True if username == current_user.username else False
    if u is not None:
        return render_template("./presentations.html", navi_upload=True, name=current_user.name, user=u, me=me)
    else:
        logger.info("Запрошенный пользователь не найден: " + username)
        return render_template("./404.html")


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
        app.run(debug=DEBUG, host=ip, port=8080, use_reloader=False)
