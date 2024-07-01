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
from routes.tasks import tasks, run_task

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

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        if current_user.is_LTI or True:  # app.recaptcha.verify(): - disable captcha (cause no login)
            return run_task()
        else:
            abort(401)
    elif request.method == "GET":
        pack = db_methods.get_criteria_pack(current_user.criteria)
        list_of_check = pack['raw_criterions']
        file_type = current_user.file_type['type']
        check_labels_and_discrpt = {CRITERIA_INFO[file_type][check[0]]['label']: CRITERIA_INFO[file_type][check[0]]['description'] for check in list_of_check}
        formats = set(current_user.formats)
        formats = formats & ALLOWED_EXTENSIONS[file_type] if formats else ALLOWED_EXTENSIONS[file_type]
        return render_template("./upload.html", navi_upload=False, formats=sorted(formats), list_of_check=check_labels_and_discrpt)



@app.route("/recheck/<check_id>", methods=["GET"])
@login_required
def recheck(check_id):
    if not current_user.is_admin:
        abort(403)
    oid = ObjectId(check_id)
    check = db_methods.get_check(oid)

    if not check:
        abort(404)
    
    # write files (original and pdf) to filestorage
    filepath = join(UPLOAD_FOLDER, f"{check_id}.{check.filename.rsplit('.', 1)[-1]}")
    pdf_filepath = join(UPLOAD_FOLDER, f"{check_id}.pdf")
    db_methods.write_file_from_db_file(oid, filepath)
    db_methods.write_file_from_db_file(ObjectId(check.conv_pdf_fs_id), pdf_filepath)
    
    check.is_ended = False
    db_methods.update_check(check)
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    db_methods.add_celery_task(task.id, check_id)  # mapping celery_task to check (check_id = file_id)
    if request.args.get('api'):
        return {'task_id': task.id, 'check_id': check_id}
    else:
        return redirect(url_for('results', _id=check_id))


@app.route("/tasks/<task_id>", methods=["GET"])
@login_required
def get_status(task_id):
    task_result = AsyncResult(task_id)
    result = {
        "task_id": task_id,
        "task_status": task_result.status,
        "task_result": task_result.result,
    }
    return jsonify(result), 200

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

    
@app.route("/api/results/ready/<string:_id>", methods=["GET"])
def ready_result(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return {}
    check = db_methods.get_check(oid)
    if check is not None:
        return {"is_ended": check.is_ended}


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
    # logger.info(db_methods.show_db_data())
    return render_template("./404.html")

@app.route("/")
def default():
    # db_methods.show_db_data()
    if current_user.is_authenticated:
        return redirect(url_for("upload"))
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
