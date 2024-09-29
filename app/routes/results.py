import bson
from bson import ObjectId

from flask import Blueprint, render_template

from app.db import db_methods
from app.utils import format_check
from app.root_logger import get_root_logger

from app.server_consts import TABLE_COLUMNS

results = Blueprint('results', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@results.route("/<string:_id>", methods=["GET"])
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