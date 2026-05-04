from flask import Blueprint, render_template, abort
from flask_login import login_required, current_user

from app.db.methods import criteria_pack as criteria_pack_methods


criterion_packs = Blueprint('criterion_packs', __name__, template_folder='templates', static_folder='static')


@criterion_packs.route("/", methods=["GET"])
@login_required
def criteria_packs():
    if not current_user.is_admin:
        abort(403)
    packs = criteria_pack_methods.get_criterion_pack_list()
    return render_template('./pack_list.html', packs=packs, name=current_user.name, navi_upload=True)
