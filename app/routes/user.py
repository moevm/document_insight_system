from flask import Blueprint, request
from flask_login import login_required
import app.servants.user as user

user_blueprint = Blueprint('user', __name__, template_folder='templates', static_folder='static')


@user_blueprint.route("/user", methods=["GET", "PUT", "DELETE"])
@login_required
def interact():
    if request.method == "GET":
        return user.logout()
    elif request.method == "PUT":
        return user.edit(request.json)
