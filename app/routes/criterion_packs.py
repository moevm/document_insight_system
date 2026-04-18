from flask import Blueprint, abort, render_template
from flask_login import current_user, login_required

from app.db import db_methods

criterion_packs = Blueprint('criterion_packs', __name__, template_folder='templates', static_folder='static')


@criterion_packs.route("/", methods=["GET"])
@login_required
def criteria_packs():
    if not current_user.is_admin:
        abort(403)
    packs = db_methods.get_criterion_pack_list()
    return render_template('./pack_list.html', packs=packs, name=current_user.name, navi_upload=True)
