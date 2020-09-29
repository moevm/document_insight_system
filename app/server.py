from flask import Flask, request
import app.user.user as user
import app.main.main as main

app = Flask(__name__)


# User pages request handlers:

@app.route("/login")
def login():
    return user.login(request.args)


@app.route("/signup")
def signup():
    return user.signup(request.args)


# Main pages request handlers:

@app.route("/upload")
def upload():
    return main.upload(request.args)


@app.route("/results")
def results():
    return main.results(request.args)


@app.route("/criteria")
def criteria():
    return main.criteria(request.args)


# Redirection:

@app.route("/")
def default():
    return "redirect to where?"


if __name__ == '__main__':
    app.run(debug=True, port=8080)
