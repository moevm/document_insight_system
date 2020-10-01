from flask import Flask, request, redirect, url_for
import app.user.user as user
import app.main.main as main

app = Flask(__name__, static_folder="./../public/")


# User pages request handlers:

@app.route("/login")
def login():
    user.login(request.args)
    return app.send_static_file("./views/login.html")


@app.route("/signup")
def signup():
    user.signup(request.args)
    return app.send_static_file("./views/signup.html")


# Main pages request handlers:

@app.route("/upload")
def upload():
    main.upload(request.args)
    return app.send_static_file("./views/upload.html")


@app.route("/results")
def results():
    main.results(request.args)
    return app.send_static_file("./views/results.html")


@app.route("/criteria")
def criteria():
    main.criteria(request.args)
    return app.send_static_file("./views/criteria.html")


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
