import bson
from bson import ObjectId
from time import time

from flask import Blueprint, Response, render_template
from flask_login import current_user, login_required
from wsgiref.handlers import format_date_time as format_date

from app.db.methods import check as check_methods
from app.db.methods import celery_check as celery_check_methods

from app.utils import format_check
from app.root_logger import get_root_logger

from app.server_consts import TABLE_COLUMNS

results_bp = Blueprint('results', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


def is_equal_username(name1: str, name2: str) -> bool:
    if name1 == name2:
        # direct comparison
        return True
    else:
        # username can be string like '<lms_login>_<lms_domen>
        # if lms_login is equal -> accept, else no
        lms_name1 = name1.split('_', 1)[0]
        lms_name2 = name2.split('_', 1)[0]
        return lms_name1 == lms_name2


@results_bp.route("/<string:_id>", methods=["GET"])
@login_required
def results_main(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return render_template("./404.html")
    check = check_methods.get_check(oid)
    if check is not None:
        # show check only for author or admin or api_access_token
        if (
            current_user.is_admin
            or is_equal_username(current_user.username, check.user)
            or check.user == "api_access_token"
        ):
            # show processing time for user
            avg_process_time = None if check.is_ended else celery_check_methods.get_average_processing_time()
            return render_template("./results.html", navi_upload=True, results=check,
                                columns=TABLE_COLUMNS, avg_process_time=avg_process_time,
                                stats=format_check(check.pack()))
        else:
            return "У вас нет прав на просмотр результатов чужих проверок", 403
    else:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return render_template("./404.html")


@results_bp.route("/svg/<string:_id>", methods=["GET"])
def results_svg(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return "InvalidId of check", 404
    check = check_methods.get_check(oid)
    if check is not None:
        result_proportion = check.get_proportion()
        if check.is_ended:
            svg_text = f"""
            <svg width="350" height="45" style="background-color: white" xmlns="http://www.w3.org/2000/svg">
                <text xml:space="preserve" text-anchor="start" font-size="20" id="title" y="25" x="10" stroke-width="0" stroke="#000" fill="#000000">Результат:</text>
                <text xml:space="preserve" text-anchor="start" font-size="20" id="result" y="25" x="110" stroke-width="0" stroke="#000" fill="#000000">{result_proportion[0]}/{result_proportion[1]}</text>
                <text xml:space="preserve" text-anchor="start" font-size="20" id="result_msg" y="25" x="200" stroke-width="0" stroke="#000" fill="#{'00FF00' if check.is_passed else 'FF0000'}">{'' if check.is_passed else 'не '}пройдена</text>
            </svg>
            """
        else:
            svg_text = f"""
            <svg width="350" height="45" style="background-color: white" xmlns="http://www.w3.org/2000/svg">
                <text xml:space="preserve" text-anchor="start" font-size="20" id="title" y="25" x="10" stroke-width="0" stroke="#000" fill="#000000">Работа проверяется</text>
            </svg>
            """
        return Response(svg_text, headers=[("Cache-Control", "no-cache"), ('Expires', format_date(time()-3600))], mimetype='image/svg+xml')
    else:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return "No such check", 404
