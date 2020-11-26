from flask import Flask, request, redirect, url_for, render_template, jsonify
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from uuid import uuid4

import app.user.user as user
import app.main.main as main
from app.bd_helper.bd_helper import get_user, delete_user

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

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("./login.html", navi_upload=False)
    elif request.method == "POST":
        u = user.login(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        return render_template("./signup.html", navi_upload=False)
    elif request.method == "POST":
        u = user.signup(request.json)
        return u.username if u is not None and login_user(u, remember=True) else ""


@app.route("/user", methods=["GET", "PUT", "DELETE"])
@login_required
def interact():
    r = request
    if request.method == "GET":
        return user.logout()
    elif request.method == "PUT":
        return user.edit(request.json)
    elif request.method == "DELETE":
        return user.signout()


# Main pages request handlers:

@app.route("/upload", methods=["GET", "POST"])
@login_required
def upload():
    if request.method == "POST":
        return jsonify(main.upload(request, UPLOAD_FOLDER))
    elif request.method == "GET":
        return render_template("./upload.html", debug=True, navi_upload=False, name=current_user.name)


@app.route("/results", methods=["GET"])
@login_required
def results():
    result = main.results(request.args)
    return render_template("./results.html", navi_upload=True, name=current_user.name, results=result)


@app.route("/criteria", methods=["GET"])
@login_required
def criteria():
    return render_template("./criteria.html", navi_upload=True, name=current_user.name)


@app.route('/profile', methods=["GET"], defaults={'username': ''})
@app.route('/profile/<string:username>')
@login_required
def profile(username):
    if username == '':
        return redirect(url_for("profile", username=current_user.username))
    u = get_user(username)
    me = True if username == current_user.username else False
    if u is not None:
        return render_template("./profile.html", navi_upload=True, name=current_user.name, user=u, me=me)
    else:
        print("No such user profile: " + username)
        return render_template("./404.html")


@app.route("/presentations", methods=["GET"], defaults={'username': ''})
@app.route('/presentations/<string:username>')
@login_required
def presentations(username):
    if username == '':
        return redirect(url_for("presentations", username=current_user.username))
    u = user.get_rich(username)
    me = True if username == current_user.username else False
    if u is not None:
        return render_template("./presentations.html", navi_upload=True, name=current_user.name, user=u, me=me)
    else:
        print("No such user presentations: " + username)
        return render_template("./404.html")


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
    print("Page /" + path + " was not found!")
    return render_template("./404.html")


@app.route("/")
def default():
    return redirect(url_for("upload"))


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
