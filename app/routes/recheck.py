from os.path import join

from bson import ObjectId

from flask import Blueprint, request, abort, redirect, url_for
from flask_login import login_required, current_user

from app.db import db_methods
from app.tasks import create_task

from app.server_consts import UPLOAD_FOLDER


recheck = Blueprint('recheck', __name__, template_folder='templates', static_folder='static')


@recheck.route("/<check_id>", methods=["GET"])
@login_required
def recheck_main(check_id):
    if not current_user.is_admin:
        abort(403)
    oid = ObjectId(check_id)
    check = db_methods.get_check(oid)

    if not check:
        abort(404)

    # write files (original and pdf) to filestorage
    filepath = join(UPLOAD_FOLDER, f"{check_id}.{check.filename.rsplit('.', 1)[-1]}")
    pdf_filepath = join(UPLOAD_FOLDER, f"{check_id}.pdf")
    db_methods.write_file_from_db_file(oid, filepath)
    db_methods.write_file_from_db_file(ObjectId(check.conv_pdf_fs_id), pdf_filepath)

    check.is_ended = False
    db_methods.update_check(check)
    task = create_task.delay(check.pack(to_str=True))  # add check to queue
    db_methods.add_celery_task(task.id, check_id)  # mapping celery_task to check (check_id = file_id)
    if request.args.get('api'):
        return {'task_id': task.id, 'check_id': check_id}
    return redirect(url_for('results.results_main', _id=check_id))
