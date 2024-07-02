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
    init_criterions, BASE_PRES_CRITERION, BASE_REPORT_CRITERION
from root_logger import get_logging_stdout_handler, get_root_logger
from servants import pre_luncher
from tasks import create_task
from utils import checklist_filter, decorator_assertion, get_file_len, format_check
from app.main.checks import CRITERIA_INFO
from routes.admin import admin
from routes.users import users
from routes.check_list import check_list
from routes.logs import logs
from routes.lti import lti
from routes.login import login
from routes.user import user_blueprint
from routes.tasks import tasks
from routes.upload import upload
from routes.recheck import recheck
from routes.results import results
from routes.api import api

from server_consts import UPLOAD_FOLDER, ALLOWED_EXTENSIONS, DOCUMENT_TYPES, TABLE_COLUMNS, URL_DOMEN

logger = get_root_logger('web')

app = Flask(__name__, static_folder="./../src/", template_folder="./templates/")
app.config.from_pyfile('settings.py')
app.recaptcha = ReCaptcha(app=app)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['CELERY_RESULT_BACKEND'] = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")
app.config['CELERY_BROKER_URL'] = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")

app.register_blueprint(admin, url_prefix='/admin')
app.register_blueprint(users, url_prefix='/users')
app.register_blueprint(check_list, url_prefix='/check_list')
app.register_blueprint(logs, url_prefix='/logs')
app.register_blueprint(lti, url_prefix='/lti')
app.register_blueprint(login, url_prefix='/login')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(tasks, url_prefix='/tasks')
app.register_blueprint(upload, url_prefix='/upload')
app.register_blueprint(recheck, url_prefix='/recheck')
app.register_blueprint(results, url_prefix='/results')
app.register_blueprint(api, url_prefix='/api')

app.logger.addHandler(get_logging_stdout_handler())
app.logger.propagate = False
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return db_methods.get_user(user_id)

# User chapters req handlers:


@decorator_assertion(app.route("/signup", methods=["GET", "POST"]), app.config["SIGNUP_PAGE_ENABLED"])
def signup():
    if request.method == "GET":
        return render_template("./signup.html", navi_upload=False)
    elif request.method == "POST":
        u = user.signup(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""


# Main chapters req handlers:

    



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

    original_names = request.args.get('original_names', False) == 'true'    

    # create tmp folder
    dirpath = tempfile.TemporaryDirectory()

    # write files
    checks_list, _ = db_methods.get_checks(**get_query(request))
    for check in checks_list:
        db_file = db_methods.find_pdf_by_file_id(check['_id'])
        original_name = db_methods.get_check(check['_id']).filename #get a filename from every check
        if db_file is not None:
            final_name = original_name if (original_name and original_names) else db_file.filename
            # to avoid overwriting files with one name and different content: now we save only last version of pres (from last check)
            if not os.path.exists(f'{dirpath.name}/{final_name}'):
                with open(f"{dirpath.name}/{final_name}", 'wb') as os_file:
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

# Когда дойду до сюда, первое задание должно быть выполнено

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
    if current_user.is_authenticated:
        return redirect(url_for("upload.upload_main"))
    else:
        return render_template("intro_page.html")


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
