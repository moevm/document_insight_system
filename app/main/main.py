from app.parser.parser import Parser
from werkzeug.utils import secure_filename
import os

parser = None


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
    with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_answer.txt', 'w') as answer:
        answer.write("".join(parser.parse_presentation()))
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
