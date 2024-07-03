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
from routes.checks import checks
from routes.logs import logs
from routes.lti import lti
from routes.login import login
from routes.user import user_blueprint
from routes.tasks import tasks
from routes.upload import upload
from routes.recheck import recheck
from routes.results import results
from routes.api import api
from routes.criterion_pack import criterion_pack
from routes.criterion_packs import criterion_packs
from routes.get_csv import get_csv
from routes.get_zip import get_zip
from routes.get_pdf import get_pdf
from routes.get_last_check_results import get_last_check_results
from routes.version import version
from routes.capacity import capacity
from routes.profile import profile

from server_consts import UPLOAD_FOLDER

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
app.register_blueprint(checks, url_prefix='/checks')
app.register_blueprint(logs, url_prefix='/logs')
app.register_blueprint(lti, url_prefix='/lti')
app.register_blueprint(login, url_prefix='/login')
app.register_blueprint(user_blueprint, url_prefix='/user')
app.register_blueprint(tasks, url_prefix='/tasks')
app.register_blueprint(upload, url_prefix='/upload')
app.register_blueprint(recheck, url_prefix='/recheck')
app.register_blueprint(results, url_prefix='/results')
app.register_blueprint(api, url_prefix='/api')
app.register_blueprint(criterion_pack, url_prefix='/criterion_pack')
app.register_blueprint(criterion_packs, url_prefix='/criterion_packs')
app.register_blueprint(get_csv, url_prefix='/get_csv')
app.register_blueprint(get_zip, url_prefix='/get_zip')
app.register_blueprint(get_pdf, url_prefix='/get_pdf')
app.register_blueprint(get_last_check_results, url_prefix='/get_last_check_results')
app.register_blueprint(version, url_prefix='/version')
app.register_blueprint(capacity, url_prefix='/capacity')
app.register_blueprint(profile, url_prefix='/profile')

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


# Когда дойду до сюда, первое задание должно быть выполнено

# Handle exceptions

@app.errorhandler(413)
def request_entity_too_large(error=None):
    return 'File exceeded the upload limit', 413


# Redirection:

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login.login_main"))

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
