import json

from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from app.db import db_methods

criterion_pack = Blueprint('criterion_pack', __name__, template_folder='templates', static_folder='static')


@criterion_pack.route("/", methods=["GET"])
@login_required
def criteria_pack_new():
    if not current_user.is_admin:
        abort(403)
    return render_template('./criteria_pack.html', name=current_user.name, navi_upload=True)



@criterion_pack.route("/<string:name>", methods=["GET"])
@login_required
def criteria_pack(name):
    if not current_user.is_admin:
        abort(403)

    pack = db_methods.get_criteria_pack(name)
    if not pack:
        abort(404)
    pack['raw_criterions'] = json.dumps(pack['raw_criterions'], indent=4, ensure_ascii=False)
    return render_template('./criteria_pack.html', pack=pack, name=current_user.name, navi_upload=True)
