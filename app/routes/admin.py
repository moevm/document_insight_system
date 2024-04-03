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
    return "There will be a list of all admin pages here"


@admin.route('/criterions', methods=["GET"])
@admin_required
def criterions():
    file_type = current_user.file_type['type']
    table_criteria = CRITERIA_INFO[file_type]
    return render_template('admin_criterions.html', table_criteria=table_criteria, file_type=file_type)


@admin.route('/criterion/<criterion_id>', methods=["GET"])
@admin_required
def criterion(criterion_id):
    return f"There will be a list of all database parametrized version of {criterion_id}"
