import json
from flask import abort, Blueprint, render_template, request, jsonify
from flask_login import current_user
from functools import wraps
from app.db.methods.user import get_user, get_user_cursor
from utils import checklist_filter, format_check_for_table

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
def users_data():
    filters = request.args.get("filter", "{}")
    try:
        filters = json.loads(filters)
        filters = filters if filters else {}
    except Exception as e:
        # logger.warning("Can't parse filters")
        # logger.warning(repr(e))
        filters = {}
    filter_query = {}
    if f_username := filters.get("username", None):
        filter_query["username"] = {"$regex": f_username}

    if f_name := filters.get("name", None):
        filter_query["name"] = {"$regex": f_name}

    if f_formats := filters.get("all_formats", None):
        filter_query["formats"] = {"$regex": f_formats}

    if f_criteria := filters.get("all_criteria", None):
        filter_query["criteria"] = {"$regex": f_criteria}

    if f_check_counts := filters.get("check_counts", None):
        try:
            f_check_counts_value, f_check_counts_cond = int(f_check_counts.split()[1]), f_check_counts.split()[0]
            if f_check_counts_cond == '>':
                filter_query["$expr"] = {"$gte": [{"$size": "$presentations"}, f_check_counts_value]}
            elif f_check_counts_cond == "<":
                filter_query["$expr"] = {"$lte": [{"$size": "$presentations"}, f_check_counts_value]}
        except ValueError:
            pass

    limit = request.args.get("limit", "")
    limit = int(limit) if limit.isnumeric() else 10

    offset = request.args.get("offset", "")
    offset = int(offset) if offset.isnumeric() else 0

    sort = request.args.get("sort", "")
    sort = 'username' if not sort else sort

    order = request.args.get("order", "")
    order = 'username' if not order else order

    rows, count = get_user_cursor(filter=filter_query, limit=limit, offset=offset, sort=sort, order=order)

    response = {
        "total": count,
        "rows": [{
            "username": item["username"],
            "name": item["name"],
            "all_formats": item["formats"],
            "all_criteria": item["criteria"],
            "check_counts": len(item["presentations"]),

        } for item in rows]
    }
    return jsonify(response)


@users.route('/', methods=["GET"])
@admin_required
def index():
    return render_template('user_list.html')


@users.route('/<username>', methods=["GET"])
@admin_required
def user_info(username):
    user_info = get_user(username)
    return render_template('one_user_info.html', user_info=user_info)
