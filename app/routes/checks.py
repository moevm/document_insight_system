import bson
from bson import ObjectId

from flask import Blueprint, render_template, Response
from flask_login import login_required

from app.db import db_main
from app.db.methods import file as file_methods
from app.root_logger import get_root_logger


checks = Blueprint('checks', __name__, template_folder='templates', static_folder='static')
logger = get_root_logger('web')


@checks.route("/<string:_id>", methods=["GET"])
@login_required
def checks_main(_id):
    try:
        f = file_methods.get_file_by_check(ObjectId(_id))
    except bson.errors.InvalidId:
        logger.error('_id exception in checks occured:', exc_info=True)
        return render_template("./404.html")
    if f is not None:
        n = 'txt/plain'
        if f.name.endswith('.ppt'):
            n = 'application/vnd.ms-powerpoint'
        elif f.name.endswith('.pptx'):
            n = 'application/vnd.openxmlformats-officedocument.presentationml.presentations'
        elif f.name.endswith('.odp'):
            n = 'application/vnd.oasis.opendocument.presentations'
        return Response(f.read(), mimetype=n)
    else:
        logger.info("Запрошенная презентация не найдена: " + _id)
        return render_template("./404.html")
