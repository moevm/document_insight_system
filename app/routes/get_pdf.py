import bson
from bson import ObjectId

from flask import Blueprint, Response, render_template
from flask_login import login_required

from app.db import db_methods
from app.db.methods import file as file_methods

from app.root_logger import get_root_logger

get_pdf = Blueprint('get_pdf', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@get_pdf.route("/<string:_id>", methods=["GET"])
@login_required
def get_pdf_main(_id):
    try:
        file = file_methods.find_pdf_by_file_id(ObjectId(_id))
    except bson.errors.InvalidId:
        logger.error('_id exception in fetching pdf occured:', exc_info=True)
        return render_template("./404.html")
    if file is not None:
        return Response(file.read(), mimetype='application/pdf')
    else:
        logger.info(f'pdf файл для проверки {id} не найден')
        return render_template("./404.html")