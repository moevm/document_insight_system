import logging
from sys import argv

import bson
from bson import ObjectId
from flask import Flask, request, redirect, url_for, render_template, Response, abort
from flask_login import LoginManager, login_user, current_user, login_required


import app.servants.user as user
from app.servants import data as data
from app.bd_helper.bd_helper import (
    get_user, get_check, get_presentation_check, users_collection,
    get_stats, get_stats_for_one_submission)
from app.servants import pre_luncher

from app.utils.decorators import condition

from flask_recaptcha import ReCaptcha

from logging import getLogger
logger = getLogger('root')
logger.setLevel(logging.DEBUG)

DEBUG = True

ALLOWED_EXTENSIONS = {'pptx', 'odp', 'ppt'}
UPLOAD_FOLDER = './files'
columns = ['Solution', 'User', 'Check added', 'Score']

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


@condition(app.route("/signup", methods=["GET", "POST"]), app.config["SIGNUP_PAGE_ENABLED"])
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
    c = get_check(oid)
    stats = get_stats_for_one_submission(oid, current_user.username)           #
    f = get_presentation_check(oid)
    if c is not None:
        return render_template("./results.html", navi_upload=True, name=current_user.name, results=c, id=_id, fi=f.name,columns=columns, stats = stats)
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
        get_all_users = users_collection.find({})
        stats = []
        for user in get_all_users:
            login = str(user['username'])
            temp = get_stats(user, login)
            stats.extend(temp)

        return render_template("./stats.html", name=current_user.name, columns = columns, stats = stats)
    else:
         login = current_user.username
         user = users_collection.find_one({'username': login})
         stats = get_stats(user, login)
         return render_template("./stats.html", name=current_user.name, columns = columns, stats = stats)



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
