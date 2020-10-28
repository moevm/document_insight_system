from flask import Flask, request, redirect, url_for, render_template
import app.user.user as user
import app.main.main as main


ALLOWED_EXTENSIONS = {'pptx', 'odp', 'ppt'}
UPLOAD_FOLDER = '../files'

app = Flask(__name__, static_folder="./../public/", template_folder="./../templates/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# User pages request handlers:

@app.route("/login", methods=["GET"])
def login():
    user.login(request.args)
    return render_template("./login.html", navi_upload=True, logout=False, name=(" ", " "))


@app.route("/signup", methods=["GET"])
def signup():
    user.signup(request.args)
    return render_template("./signup.html", navi_upload=True, logout=False, name=(" ", " "))


# Main pages request handlers:

@app.route("/upload", methods=["GET", "POST"])
def upload():
    if request.method == "POST":
        return str(main.upload(request, UPLOAD_FOLDER))
    elif request.method == "GET":
        return render_template("./upload.html", debug=True, navi_upload=False, logout=True, name=("Имя", "Фамилия"))


@app.route("/results", methods=["GET"])
def results():
    main.results(request.args)
    return render_template("./results.html", navi_upload=True, logout=True, name=("Имя", "Фамилия"))


@app.route("/criteria", methods=["GET"])
def criteria():
    main.criteria(request.args)
    return render_template("./criteria.html", navi_upload=True, logout=True, name=("Имя", "Фамилия"))


@app.route("/status", methods=["GET"])
def status():
    return str(main.status())


# Redirection:

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
