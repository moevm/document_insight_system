from flask import Blueprint, request, render_template
from flask_login import login_user
import app.servants.user as user

login = Blueprint('login', __name__, template_folder='templates', static_folder='static')


@login.route("/", methods=["GET", "POST"])
def login_main():
    if request.method == "GET":
        return render_template("./login.html", navi_upload=False)
    elif request.method == "POST":
        u = user.login(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""
