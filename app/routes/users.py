from flask import abort, Blueprint, render_template, request, jsonify
from flask_login import current_user
from functools import wraps
from app.db.db_methods import get_all_users, get_user
from utils import checklist_filter, format_check_for_table
from db import db_methods

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')


def admin_required(route_func):
    @wraps(route_func)
    def my_wrapper(*args, **kwargs):
        if current_user and current_user.is_admin:
            return route_func(*args, **kwargs)
        abort(403)
    return my_wrapper



@users.route("/data")
@admin_required
def user_list_data():
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


@users.route('/', methods=["GET"])
@admin_required
def index():
    users = list(get_all_users())
    usernames = [(user['name'], user['username']) for user in users]
    return render_template('user_list.html', usernames=usernames)

@users.route('/<username>', methods=["GET"])
@admin_required
def user_info(username):
    user_info = get_user(username)
    return render_template('one_user_info.html', user_info=user_info, check_counts = len(user_info.presentations))
