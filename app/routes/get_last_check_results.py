import bson
from bson import ObjectId

from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required

from app.db.methods import check as check_methods
from app.root_logger import get_root_logger


get_last_check_results = Blueprint('get_last_check_results', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@get_last_check_results.route("/<string:moodle_id>", methods=["GET"])
@login_required
def get_latest_user_check(moodle_id):
    check = check_methods.get_latest_user_check_by_moodle(moodle_id)
    logger.error(str(check))
    if check:
        check = check[0]
        return redirect(url_for('results.results_main', _id=str(check['_id'])))
    else:
        return render_template("./404.html")
