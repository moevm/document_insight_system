tags = {'br': '<br>', 'close_div': '</div>', 'div_class': '<div class="format_description">'}

def format_descriptions(desc_list, open_tag = '', close_tag = ''):
    return list(map(lambda item: open_tag + item + close_tag, desc_list))

def format_header(header, close_tag = ''):
    return header + close_tag

def find_tasks_on_slides_feedback(slides_with_tasks):
    return format_header('Всего задач: {}'.format(slides_with_tasks.get('count')), tags.get('br')), \
           'Распознанные задачи: ', \
           *format_descriptions(slides_with_tasks.get('recognized'), tags.get('div_class'), tags.get('br') + tags.get('close_div')), \
           'Не найдены: ', \
           *format_descriptions(slides_with_tasks.get('not_found'), tags.get('div_class'), tags.get('br') + tags.get('close_div'))

def tasks_conclusions_feedback(results):
    return format_header('Соответствует на {}%'.format(results[0]), tags.get('br')), \
           'Распознанные заключения: ', \
            *format_descriptions(results[2], tags.get('div_class'), tags.get('br') + tags.get('close_div'))
