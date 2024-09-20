import bson
from bson import ObjectId

from flask import Blueprint, Response, render_template

from app.db import db_methods
from app.utils import format_check
from app.root_logger import get_root_logger

from app.server_consts import TABLE_COLUMNS

results_bp = Blueprint('results', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@results_bp.route("/<string:_id>", methods=["GET"])
def results_main(_id):
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
    
@results_bp.route("/svg/<string:_id>", methods=["GET"])
def results_svg(_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return "InvalidId of check", 404
    check = db_methods.get_check(oid)
    if check is not None:
        result_proportion = check.get_proportion()
        svg_text = f"""
        <svg width="300" height="50" xmlns="http://www.w3.org/2000/svg">
            <text xml:space="preserve" text-anchor="start" font-size="20" id="title" y="25" x="10" stroke-width="0" stroke="#000" fill="#000000">Результат:</text>
            <text xml:space="preserve" text-anchor="start" font-size="20" id="result" y="25" x="100" stroke-width="0" stroke="#000" fill="#000000">{result_proportion[0]}/{result_proportion[1]}</text>
            <text xml:space="preserve" text-anchor="start" font-size="20" id="result_msg" y="25" x="170" stroke-width="0" stroke="#000" fill="#{'00' if check.is_passed else 'FF'}0000">{'' if check.is_passed else 'не '}пройдена</text>
        </svg>
        """
        return Response(svg_text, mimetype='image/svg+xml')
    else:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return "No such check", 404