from bson import ObjectId
from flask_login import current_user

from app.bd_helper.bd_helper import create_check, add_check, add_presentation, get_presentation, get_check, \
    delete_presentation, find_presentation
from app.parser.parser import Parser
from werkzeug.utils import secure_filename
import os


SLIDE_GOALS_AND_TASKS = 'Цель и задачи'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_CONCLUSION = 'Заключение'


def _collect_results(status, checks_id):
    return {
        "status": status,
        "id": str(checks_id)
    }


def upload(request, upload_folder):
    if request.json is not None and request.json['file_name'] is not None:
        filename = request.json['file_name']
    else:
        if "presentation" not in request.files:
            print("Поступил пустой запрос")
            return _collect_results(-1, None)
        file = request.files["presentation"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, file.filename))

    presentation_name = os.path.splitext(filename)[0]
    presentation = find_presentation(current_user, presentation_name)
    if presentation is None:
        user, presentation_id = add_presentation(current_user, presentation_name)
        presentation = get_presentation(presentation_id)

    parser = Parser(upload_folder + '/' + filename)
    result = []
    try:
        with open(upload_folder + '/' + presentation_name + '_answer.txt', 'w') as answer:
            for line in parser.get_text():
                answer.write(line)
    except Exception as err:
        print(err)
        print("Что-то пошло не так")
        return -1

    result.append(-1)  # Количество основных слайдов

    slides_enumeration = parser.check_slides_enumeration()
    result.append(slides_enumeration)  # Нумерация слайдов

    titles_size = parser.check_title_size(filename, upload_folder)
    result.append(titles_size)  # Заголовки слайдов занимают не более двух строк

    try:
        with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_definite_slides.txt', 'w') as definite_slides:
            buf = parser.find_definite_slide(SLIDE_GOALS_AND_TASKS)
            if buf:
                definite_slides.write(SLIDE_GOALS_AND_TASKS + ':' + str(buf) + '\n')
                result.append(str(buf))  # Слайд "Цель и задачи"
            else:
                result.append("")

            buf = parser.find_definite_slide(SLIDE_APPROBATION_OF_WORK)
            if buf:
                definite_slides.write(SLIDE_APPROBATION_OF_WORK + ':' + str(buf) + '\n')
                result.append(str(buf))  # Слайд "Апробация работы"
            else:
                result.append("")

            result.append(-1)  # Слайд с описанием актуальности работы

            buf = parser.find_definite_slide(SLIDE_CONCLUSION)
            if buf:
                definite_slides.write(SLIDE_CONCLUSION+':' + str(buf) + '\n')
                result.append(str(buf))  # Слайд с заключением
            else:
                result.append("")

    except Exception as err:
        print(err)
        print("Что-то пошло не так")
        return _collect_results(-1, None)
    if parser.get_state() == -1:
        print("Что-то пошло не так")
    elif parser.get_state() == 3:
        print("Презентация обработана")

    checks = create_check(result[0], result[1], result[2], result[3], result[4], result[5], result[6])
    presentation, checks_id = add_check(presentation, checks)

    return _collect_results(parser.get_state(), checks_id)


def remove_presentation(json):
    count = len(current_user.presentations)
    user, presentation = delete_presentation(current_user, ObjectId(json['presentation']))
    return 'OK' if count == len(user.presentations) - 1 else 'Not OK'


def criteria(args):
    return "Criteria page, args: " + str(args)
