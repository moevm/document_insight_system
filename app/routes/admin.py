from flask import abort, Blueprint, render_template
from flask_login import current_user
from functools import wraps
from app.main.checks import CRITERIA_INFO

admin = Blueprint('admin', __name__, template_folder='templates', static_folder='static')


def admin_required(route_func):
    @wraps(route_func)
    def my_wrapper(*args, **kwargs):
        if current_user and current_user.is_admin:
            return route_func(*args, **kwargs)
        abort(403)
    return my_wrapper


@admin.route('/', methods=["GET"])
@admin_required
def index():
    return render_template('admin_pages_list.html')


@admin.route('/criterions', methods=["GET"])
@admin_required
def criterions():
    table_criteria = CRITERIA_INFO
    return render_template('admin_criterions.html', table_criteria=table_criteria)


@admin.route('/criterion/<criterion_id>', methods=["GET"])
@admin_required
def criterion(criterion_id):
    return f"There will be a list of all database parametrized version of {criterion_id}"
