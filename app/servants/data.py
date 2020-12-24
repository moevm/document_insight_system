from os import remove
from os.path import join, exists
from bson import ObjectId
from flask_login import current_user

from app.bd_helper.bd_helper import *
from app.main.checker import check
from app.main.parser import parse

DEFAULT_PRESENTATION = 'sample.odp'


def upload(request, upload_folder):
    try:
        if "presentation" in request.files:
            file = request.files["presentation"]
            filename = join(upload_folder, file.filename)
            file.save(filename)
            delete = True
        else:
            filename = join(upload_folder, DEFAULT_PRESENTATION)
            delete = False

        presentation_name = basename(filename)
        print("Обработка презентации " + presentation_name + " пользователя " +
              current_user.username + " проверками " + str(current_user.criteria))
        presentation = find_presentation(current_user, presentation_name)
        if presentation is None:
            user, presentation_id = add_presentation(current_user, presentation_name)
            presentation = get_presentation(presentation_id)

        checks = create_check(current_user)
        check(parse(filename), checks)
        presentation, checks_id = add_check(presentation, checks, filename)

        if delete and exists(filename):
            remove(filename)

        print("\tОбработка завершена успешно!")
        return str(checks_id)
    except Exception as e:
        print("\tПри обработке произошла ошибка: " + str(e))
        return 'Not OK'


def remove_presentation(json):
    count = len(current_user.presentations)
    user, presentation = delete_presentation(current_user, ObjectId(json['presentation']))
    deleted = count == len(user.presentations) - 1
    print("Презентация " + presentation.name + " пользователя " + user.username + " удалена со всеми проверками")
    return 'OK' if deleted else 'Not OK'
