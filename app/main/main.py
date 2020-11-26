from app.parser.parser import Parser
from werkzeug.utils import secure_filename
import os


parser = None
result = []
SLIDE_GOALS_AND_TASKS = 'Цель и задачи'
SLIDE_APPROBATION_OF_WORK = 'Апробация'
SLIDE_CONCLUSION = 'Заключение'


def upload(request, upload_folder):
    global parser
    global result

    if request.json is not None and request.json['file_name'] is not None:
        filename = request.json['file_name']
    else:
        if "presentation" not in request.files:
            print("Поступил пустой запрос")
            return -1
        file = request.files["presentation"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(upload_folder, file.filename))
    parser = Parser(upload_folder + '/' + filename)
    result = []
    try:
        with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_answer.txt', 'w') as answer:
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
                with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_goals_and_tasks.txt',
                          'w') as goals_and_tasks:
                    goals_and_tasks.write(parser.text[buf-1])
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
                with open(upload_folder + '/' + os.path.splitext(filename)[0] + '_conclusion.txt',
                          'w') as conclusion:
                    conclusion.write(parser.text[buf-1])
            else:
                result.append("")

    except Exception as err:
        print(err)
        print("Что-то пошло не так")
        return -1
    if parser.get_state() == -1:
        print("Что-то пошло не так")
    elif parser.get_state() == 3:
        print("Презентация обработана")

    satisfied = True
    for crit in result:
        satisfied &= crit == "" or crit == -1
    result.append(satisfied)

    print(parser.is_slides_similar(upload_folder + '/' + os.path.splitext(filename)[0] + '_goals_and_tasks.txt', upload_folder + '/' + os.path.splitext(filename)[0] + '_conclusion.txt'))
    return parser.get_state()


def results(args):
    return result


def criteria(args):
    return "Criteria page, args: " + str(args)


def status():
    global parser
    if parser is not None:
        return parser.get_state()
    else:
        return 0
