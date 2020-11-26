from os.path import splitext, join
from bson import ObjectId
from flask_login import current_user
from werkzeug.utils import secure_filename

from app.bd_helper.bd_helper import *
from app.main.checker import check
from app.main.parser import parse

DEFAULT_PRESENTATION = 'sample.odp'


def upload(request, upload_folder):
    try:
        if "presentation" in request.files:
            file = request.files["presentation"]
            filename = secure_filename(file.filename)
            file.save(join(upload_folder, file.filename))
        else:
            filename = DEFAULT_PRESENTATION

        presentation_name = splitext(filename)[0]
        presentation = find_presentation(current_user, presentation_name)
        if presentation is None:
            user, presentation_id = add_presentation(current_user, presentation_name)
            presentation = get_presentation(presentation_id)

        checks = create_check()
        check(parse(upload_folder + '/' + filename), checks)

        presentation, checks_id = add_check(presentation, checks)
        return str(checks_id)
    except Exception:
        return ""


def remove_presentation(json):
    count = len(current_user.presentations)
    user, presentation = delete_presentation(current_user, ObjectId(json['presentation']))
    return 'OK' if count == len(user.presentations) - 1 else 'Not OK'


def criteria(args):
    return "Criteria page, args: " + str(args)
