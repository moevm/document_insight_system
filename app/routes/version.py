from flask import Blueprint, render_template


version = Blueprint('version', __name__, template_folder='templates', static_folder='static')


@version.route("/")
def version_main():
    return render_template("./version.html")