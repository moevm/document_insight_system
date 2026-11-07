from functools import wraps

from flask import Blueprint, abort, jsonify, render_template, request
from flask_login import current_user

from app.db.methods.user import get_user, get_user_cursor
from app.utils.table_query import number_filter, page_options, read_filters, text_filter

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')


def admin_required(route_func):
    @wraps(route_func)
    def my_wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            abort(401)
        if not current_user.is_admin:
            abort(403)
        return route_func(*args, **kwargs)

    return my_wrapper


@users.route("/data")
@admin_required
def users_data():
    try:
        filters = read_filters(request.args)
        filter_query = {}
        for field, key in {
            'username': 'username',
            'name': 'name',
            'all_criteria': 'criteria',
        }.items():
            if value := filters.get(field):
                filter_query[key] = text_filter(value)
        if file_format := filters.get('all_formats'):
            filter_query['formats'] = file_format.lower()
        if role := filters.get('role'):
            if role not in ('admin', 'user'):
                raise ValueError('Неизвестная роль.')
            filter_query['is_admin'] = True if role == 'admin' else {'$ne': True}
        if is_lti := filters.get('is_LTI'):
            if is_lti not in ('true', 'false'):
                raise ValueError('Неизвестный способ входа.')
            filter_query['is_LTI'] = True if is_lti == 'true' else {'$ne': True}
        if count := filters.get('check_counts'):
            condition = number_filter(count, integer=True)
            count_expr = {'$size': {'$ifNull': ['$files', []]}}
            filter_query['$expr'] = (
                {'$and': [{op: [count_expr, value]} for op, value in condition.items()]}
                if isinstance(condition, dict)
                else {'$eq': [count_expr, condition]}
            )
        if search := request.args.get('search', '').strip():
            filter_query['$or'] = [{field: text_filter(search)} for field in ('username', 'name', 'criteria')]
        options = page_options(
            request.args,
            {'username', 'name', 'role', 'is_LTI', 'all_formats', 'all_criteria', 'check_counts'},
            'username',
        )
    except ValueError as error:
        return jsonify(error=str(error)), 400
    rows, count = get_user_cursor(filter=filter_query, **options)

    response = {
        "total": count,
        "rows": [
            {
                "username": item["username"],
                "name": item.get("name", ''),
                "role": "Администратор" if item.get("is_admin", False) else "Пользователь",
                "is_LTI": item.get("is_LTI", False),
                "all_formats": item.get("formats", []),
                "all_criteria": item.get("criteria", ''),
                "check_counts": len(item.get("files") or []),
            }
            for item in rows
        ],
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
    if user_info is None:
        abort(404)
    return render_template('one_user_info.html', user_info=user_info)
