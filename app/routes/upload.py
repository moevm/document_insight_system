from flask import Blueprint, request, abort, render_template
from flask_login import login_required, current_user
from flask import current_app

from app.db import db_methods

from app.server_consts import ALLOWED_EXTENSIONS
from app.main.checks import CRITERIA_INFO
from app.routes.tasks import run_task


upload = Blueprint('upload', __name__, template_folder='templates', static_folder='static')


@upload.route("/", methods=["GET", "POST"])
@login_required
def upload_main():
    if request.method == "POST":
        if current_user.is_LTI or True:  # app.recaptcha.verify(): - disable captcha (cause no login)
            return run_task()
        else:
            abort(401)
    elif request.method == "GET":
        pack = db_methods.get_criteria_pack(current_user.criteria)
    list_of_check = pack['raw_criterions']
    file_type = current_user.file_type['type']
    check_labels_and_discrpt = {
        CRITERIA_INFO[file_type][check[0]]['label']: CRITERIA_INFO[file_type][check[0]]['description']
        for check in list_of_check
    }
    formats = set(current_user.formats)
    formats = formats & ALLOWED_EXTENSIONS[file_type] if formats else ALLOWED_EXTENSIONS[file_type]

    role = "admin" if current_user.is_admin else "user"
    base_url = current_app.config.get("TEMPLATER_URL", "http://localhost:8092")
    templater_url = f"{base_url}?role={role}"



    return render_template(
        "./upload.html",
        navi_upload=False,
        formats=sorted(formats),
        list_of_check=check_labels_and_discrpt,
        templater_url=templater_url
    )

