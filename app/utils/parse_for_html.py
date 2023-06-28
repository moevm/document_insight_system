from argparse import Namespace

tags = {'br': '<br>', 'close_div': '</div>', 'div_class': '<div class="format_description">'}
tag = Namespace(**tags)


def format_descriptions(desc_list, open_tag='', close_tag=''):
    return list(map(lambda item: f"{open_tag}{item}{close_tag}", desc_list))


def format_header(header, close_tag=tag.br):
    return f"{header}{close_tag}"


def find_tasks_on_slides_feedback(slides_with_tasks):
    return (format_header('Всего задач: {}'.format(slides_with_tasks.get('count')), tag.br),
            'Распознанные задачи на слайде "Цель и задачи": ',
            *format_descriptions(slides_with_tasks.get('recognized'), tag.div_class, tag.br + tag.close_div),
            'Не найдены соответствующие слайды для задач: ',
            *format_descriptions(slides_with_tasks.get('not_found'), tag.div_class, tag.br + tag.close_div),
            'Попробуйте перефразировать название слайда, чтобы оно больше подходило к задаче')


def tasks_conclusions_feedback(results):
    return format_header('Соответствует на {}%'.format(results[0]), tag.br), \
           'Распознанные заключения: ', \
           *format_descriptions(results[2], tag.div_class, tag.br + tag.close_div)
