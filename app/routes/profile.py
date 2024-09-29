from flask import Blueprint, abort
from flask_login import login_required


profile = Blueprint('profile', __name__, template_folder='templates', static_folder='static')


@profile.route('/', methods=["GET"], defaults={'username': ''})
@profile.route('/<string:username>', methods=["GET"])
@login_required
def profile_main(username):
    return abort(404)
    # if current_user.is_admin:
    #     if username == '':
    #         return redirect(url_for("profile", username=current_user.username))
    #     u = db_methods.get_user(username)
    #     me = True if username == current_user.username else False
    #     if u is not None:
    #         return render_template("./profile.html", navi_upload=True, name=current_user.name, user=u, me=me)
    #     else:
    #         logger.info("Запрошенный пользователь не найден: " + username)
    #         return render_template("./404.html")
    # else:
    #     abort(403)

