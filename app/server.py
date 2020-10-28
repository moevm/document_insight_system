from flask import Flask, request, redirect, url_for, render_template
import app.user.user as user
import app.main.main as main


ALLOWED_EXTENSIONS = {'pptx', 'odp', 'ppt'}
UPLOAD_FOLDER = '../files'

app = Flask(__name__, static_folder="./../public/", template_folder="./../templates/")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# User pages request handlers:

@app.route("/login")
def login():
    user.login(request.args)
    return render_template("./login.html")


@app.route("/signup")
def signup():
    user.signup(request.args)
    return render_template("./signup.html")


# Main pages request handlers:

@app.route("/upload")
def upload():
    main.upload(request.args)
    return render_template("./upload.html")


@app.route("/results")
def results():
    main.results(request.args)
    return render_template("./results.html")


@app.route("/criteria", methods=['GET', 'POST'])
def criteria():
    if request.method == 'POST':
        file = request.files['presentation']
        main.parse_presentation(app, file, UPLOAD_FOLDER)
    main.criteria(request.args)
    return render_template("./criteria.html")


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
