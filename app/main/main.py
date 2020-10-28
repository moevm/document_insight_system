from app.parser.parser import Parser
from werkzeug.utils import secure_filename
import os


def upload(args):
    return "Upload page, args: " + str(args)


def results(args):
    return "Results page, args: " + str(args)


def criteria(args):
    return "Criteria page, args: " + str(args)


def parse_presentation(app, file, upload_folder):
    filename = secure_filename(file.filename)
    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
    parser = Parser(upload_folder + '/' + filename)
    if parser.get_state() == -1:
        print("Что-то пошло не так")
    elif parser.get_state() == 1:
        print("Презентация загружена")
    elif parser.get_state() == 2:
        print("Презентация обработана")
    try:
        with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_answer.txt', 'w') as answer:
            for line in parser.get_text():
                answer.write(line)
    except Exception as err:
        print(err)
        print("Что-то пошло не так")
    parser.check_title_size(filename, upload_folder)
