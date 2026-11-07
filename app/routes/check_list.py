from flask import Blueprint, jsonify, render_template, request
from flask_login import current_user, login_required

from app.db.methods import check as check_methods
from app.utils import checklist_filter, format_check_for_table
from app.utils.table_query import page_options

check_list = Blueprint('check_list', __name__, template_folder='templates', static_folder='static')


@check_list.route("/")
@login_required
def check_list_main():
    return render_template("./check_list.html", name=current_user.name, navi_upload=True)


@check_list.route("/data")
@login_required
def check_list_data():
    data = request.args.copy()
    try:
        filter_query = checklist_filter(data)
        options = page_options(
            data, {'filename', 'criteria', 'user', 'upload-date', 'moodle-date', 'score'}, 'upload-date', 'desc'
        )
    except ValueError as error:
        return jsonify(error=str(error)), 400
    if options['sort'] == 'upload-date':
        options['sort'] = '_id'
    query = dict(filter=filter_query, **options)

    if data.get("latest"):
        rows, count = check_methods.get_latest_check_cursor(**query)
    else:
        # get data and records count
        rows, count = check_methods.get_checks_cursor(**query)

    # construct response
    response = {"total": count, "rows": [format_check_for_table(item, include_status=True) for item in rows]}

    # return json data
    return jsonify(response)
