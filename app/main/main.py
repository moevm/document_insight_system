from app.parser.parser import Parser
from werkzeug.utils import secure_filename
import os


parser = None
SLIDE_CONCLUSION = 'Заключение'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_GOALS_AND_TASKS = 'Цель и задачи'


def upload(request, upload_folder):
    global parser
    filename = request.data.decode("utf-8")
    if filename != "":
        filename = filename.split("=")[1]
    else:
        if "presentation" not in request.files:
            print("Поступил пустой запрос")
            return -1
        file = request.files["presentation"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, file.filename))
    parser = Parser(upload_folder + '/' + filename)
    try:
        with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_answer.txt', 'w') as answer:
            for line in parser.get_text():
                answer.write(line)
    except Exception as err:
        print(err)
        print("Что-то пошло не так")
        return -1
    parser.check_title_size(filename, upload_folder)
    try:
        with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_definite_slides.txt', 'w') as definite_slides:
            buf = parser.find_definite_slide(SLIDE_CONCLUSION)
            if buf:
                definite_slides.write(SLIDE_CONCLUSION+':' + str(buf) + '\n')
            buf = parser.find_definite_slide(SLIDE_GOALS_AND_TASKS)
            if buf:
                definite_slides.write(SLIDE_GOALS_AND_TASKS+':' + str(buf) + '\n')
            buf = parser.find_definite_slide(SLIDE_APPROBATION_OF_WORK)
            if buf:
                definite_slides.write(SLIDE_APPROBATION_OF_WORK+':' + str(buf) + '\n')
    except Exception as err:
        print(err)
        print("Что-то пошло не так")
        return -1
    if parser.check_enumeration(filename, upload_folder) == 0:
        print("Слайды корректно пронумерованы")
    else:
        print("Слайды пронумерованы некорректно")

    if parser.get_state() == -1:
        print("Что-то пошло не так")
    elif parser.get_state() == 3:
        print("Презентация обработана")
    return parser.get_state()


def results(args):
    return "Results page, args: " + str(args)


def criteria(args):
    return "Criteria page, args: " + str(args)


def status():
    global parser
    if parser is not None:
        return parser.get_state()
    else:
        return 0
