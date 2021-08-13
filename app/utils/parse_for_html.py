def format_descriptions(desc_list):
    return ['<div style="margin-left: 2em;">' + item + '<br></div>' for item in desc_list]

def find_tasks_on_slides_feedback(slides_with_tasks):
    return 'Всего задач: {}'.format(slides_with_tasks.get('count')) + '<br>', \
           'Распознанные задачи: ', *format_descriptions(slides_with_tasks.get('recognized')), \
           'Не найдены: ', *format_descriptions(slides_with_tasks.get('not_found'))

def tasks_conclusions_feedback(results):
    return 'Соответствует на {}%'.format(results[0]) + '<br>', \
           'Распознанные заключения: ', *format_descriptions(results[2])
