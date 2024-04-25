from flask import abort, Blueprint, render_template
from flask_login import current_user
from functools import wraps
from app.db.db_methods import get_all_users, get_user

users = Blueprint('users', __name__, template_folder='templates', static_folder='static')


def admin_required(route_func):
    @wraps(route_func)
    def my_wrapper(*args, **kwargs):
        if current_user and current_user.is_admin:
            return route_func(*args, **kwargs)
        abort(403)
    return my_wrapper


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
