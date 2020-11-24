from flask import Flask, request, redirect, url_for, render_template
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from uuid import uuid4

import app.user.user as user
import app.main.main as main
from app.bd_helper.bd_helper import get_user

ALLOWED_EXTENSIONS = {'pptx', 'odp', 'ppt'}
UPLOAD_FOLDER = '../files'

app = Flask(__name__, static_folder="./../public/", template_folder="./../templates/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = str(uuid4())

login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return get_user(user_id)


# User pages request handlers:

@app.route("/login", methods=["GET", "POST", "DELETE"])
def login():
    if request.method == "GET":
        return render_template("./login.html", navi_upload=False, logout=False)
    elif request.method == "POST":
        u = user.login(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""
    elif request.method == "DELETE":
        logout_user()
        return 'OK'


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("./signup.html", navi_upload=False, logout=False)
    elif request.method == "POST":
        u = user.signup(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""


# Main pages request handlers:

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        return str(main.upload(request, UPLOAD_FOLDER))
    elif request.method == "GET":
        return render_template("./upload.html", debug=True, navi_upload=False, logout=True, name=current_user.name)


@app.route("/results", methods=["GET"])
@login_required
def results():
    result = main.results(request.args)
    return render_template("./results.html", navi_upload=True, logout=True, name=current_user.name, results=result)


@app.route("/criteria", methods=["GET"])
@login_required
def criteria():
    return render_template("./criteria.html", navi_upload=True, logout=True, name=current_user.name)


@app.route("/status", methods=["GET"])
def status():
    return str(main.status())


# Redirection:

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for("login"))


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s' % path


@app.route("/")
def default():
    return redirect(url_for("login"))


# Disable caching:

@app.after_request
def add_header(r):
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    r.headers["Pragma"] = "no-cache"
    r.headers["Expires"] = "0"
    r.headers['Cache-Control'] = 'public, max-age=0'
    return r


if __name__ == '__main__':
    app.run(debug=True, port=8080)
