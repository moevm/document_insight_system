from flask import Blueprint, render_template, jsonify, request

from app.utils import format_check_for_table, checklist_filter
from app.db import db_methods
from flask_login import login_required, current_user

check_list = Blueprint('check_list', __name__, template_folder='templates', static_folder='static')

@check_list.route("/")
@login_required
def check_list_main():
    return render_template("./check_list.html", name=current_user.name, navi_upload=True)


@check_list.route("/data")
@login_required
def check_list_data():
    data = request.args.copy()
    filter_query = checklist_filter(data)
    # parse and validate rest query
    limit = data.get("limit", '')
    limit = int(limit) if limit.isdigit() else 10

    offset = data.get("offset", '')
    offset = int(offset) if offset.isdigit() else 0

    sort = data.get("sort")
    sort = 'upload-date' if not sort else sort

    order = data.get("order")
    order = 'desc' if not order else order

    sort = "_id" if sort == "upload-date" else sort

    query = dict(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    if data.get("latest"):
        rows, count = db_methods.get_latest_check_cursor(**query)
    else:
        # get data and records count
        rows, count = db_methods.get_checks_cursor(**query)

    # construct response
    response = {
        "total": count,
        "rows": [format_check_for_table(item) for item in rows]
    }

    # return json data
    return jsonify(response)
