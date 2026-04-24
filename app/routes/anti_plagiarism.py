import bson
from bson import ObjectId

from flask import Blueprint, render_template, url_for
from flask_login import current_user, login_required

from app.db import db_methods
from app.root_logger import get_root_logger

anti_plagiarism = Blueprint('anti_plagiarism', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@anti_plagiarism.route("/<string:_id>/<string:source_check_id>", methods=["GET"])
@login_required
def anti_plagiarism_page(_id, source_check_id):
    try:
        oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('_id exception:', exc_info=True)
        return render_template("./404.html")

    check = db_methods.get_check(oid)
    if check is None:
        logger.info("Запрошенная проверка не найдена: " + _id)
        return render_template("./404.html")

    try:
        source_oid = ObjectId(_id)
    except bson.errors.InvalidId:
        logger.error('source_check_id exception:', exc_info=True)
        return render_template("./404.html")
    source_check = db_methods.get_check(source_oid)
    if source_check is None:
        logger.info("Запрошенная проверка не найдена: " + source_check_id)
        return render_template("./404.html")
    if not (current_user.is_admin):
        return "У вас нет прав на просмотр", 403

    fragments = []

    student_pdf_url = url_for("get_pdf.get_pdf_main", _id=check.conv_pdf_fs_id)
    source_pdf_url = url_for("get_pdf.get_pdf_main", _id=source_check.conv_pdf_fs_id)

    return render_template(
        "anti_plagiarism.html",
        fragments=fragments,
        student_pdf_url=student_pdf_url,
        source_pdf_url=source_pdf_url,
    )
