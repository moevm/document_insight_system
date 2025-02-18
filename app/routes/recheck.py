from os.path import join

from bson import ObjectId

from flask import Blueprint, request, abort, redirect, url_for
from flask_login import login_required, current_user

from app.tasks import create_task
from app.db.methods import file as file_methods
from app.db.methods import check as check_methods
from app.db.methods import celery_check as celery_check_methods

from app.server_consts import UPLOAD_FOLDER


recheck = Blueprint('recheck', __name__, template_folder='templates', static_folder='static')


@recheck.route("/<check_id>", methods=["GET"])
@login_required
def recheck_main(check_id):
    if not current_user.is_admin:
        abort(403)
    oid = ObjectId(check_id)
    check = check_methods.get_check(oid)

    if not check:
        abort(404)

    # write files (original and pdf) to filestorage
    filepath = join(UPLOAD_FOLDER, f"{check_id}.{check.filename.rsplit('.', 1)[-1]}")
    pdf_filepath = join(UPLOAD_FOLDER, f"{check_id}.pdf")
    file_methods.write_file_from_db_file(oid, filepath)
    file_methods.write_file_from_db_file(ObjectId(check.conv_pdf_fs_id), pdf_filepath)

    check.is_ended = False
    check_methods.update_check(check)
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    celery_check_methods.add_celery_task(task.id, check_id)  # mapping celery_task to check (check_id = file_id)
    if request.args.get('api'):
        return {'task_id': task.id, 'check_id': check_id}
    else:
        return redirect(url_for('results', _id=check_id))

