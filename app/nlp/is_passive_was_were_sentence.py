import re
import pymorphy2
import string
from enum import Enum

morph = pymorphy2.MorphAnalyzer()


class CritreriaType(Enum):
    REPORT = 'report'
    PRESENTATION = 'pres'


def criteria_type_to_str(type: CritreriaType):
    if type == CritreriaType.REPORT:
        return "Страница"
    elif type == CritreriaType.PRESENTATION:
        return "Слайд"
    else:
        return "Элемент"

def get_content_by_file(file, type: CritreriaType):
    if type == CritreriaType.REPORT:
        return file.pdf_file.get_text_on_page().items()
    elif type == CritreriaType.PRESENTATION:
        return enumerate(file.get_text_from_slides())

def clean_word(word):
    punct = string.punctuation.replace('-', '')
    return word.translate(str.maketrans('', '', punct))


def is_passive_was_were_sentece(sentence):
    """
    Примеры плохих предложений (пассивные конструкции с "Был*" - можно убрать):
    - Был проведен анализ данных
    - Была выполнена работа по исследованию
    - Было принято решение о внедрении
    - Были получены следующие результаты
    - Была создана база данных
    
    Примеры хороших предложений ("Был*" нельзя убрать):
    - Было бы здорово получить новые данные
    - Был сильный скачок напряжения
    - Были времена, когда это казалось невозможным
    - Был студентом университета три года назад
    - Была программистом до выхода на пенсию
    """
    first_words = re.split(r'\s+', sentence.strip(), maxsplit=2)
    if len(first_words) < 2:
        return False

    first_word = clean_word(first_words[0])
    second_word = clean_word(first_words[1])

    parsed = morph.parse(first_word)[0]
    if (parsed.normal_form == 'быть' and
        'past' in parsed.tag and
        parsed.tag.POS == 'VERB'):
        second_word_parsed = morph.parse(second_word)[0]
        return ('PRTS' in second_word_parsed.tag and 
                'pssv' in second_word_parsed.tag)
    return False


def generate_output_text(detected_senteces, type: CritreriaType, format_page_link_fn=None):
    output = 'Обнаружены конструкции (Был/Была/Было/Были), которые можно удалить без потери смысла:<br><br>'
    if type == CritreriaType.REPORT:
        offset_index = 0
    elif type == CritreriaType.PRESENTATION:
        offset_index = 1
    for index, messages in detected_senteces.items():
        display_index = index + offset_index
        output_type = criteria_type_to_str(type)
        if format_page_link_fn:
            output += f'<b>{output_type} {format_page_link_fn([display_index])}:</b> <br>' + '<br>'.join(messages) + '<br><br>'
        else:
            output += f'<b>{output_type} №{display_index}:</b> <br>' + '<br>'.join(messages) + '<br><br>'
    return output


def get_was_were_sentences(file, type: CritreriaType):
    detected = {}
    total_sentences = 0
    for page_index, page_text in get_content_by_file(file, type):
        lines = re.split(r'\n', page_text)
        non_empty_line_counter = 0
        for line_index, line in enumerate(lines):
            print(line_index, line)
            line = line.strip()
            if not line:
                continue

            non_empty_line_counter += 1
            sentences = re.split(r'[.!?…]+\s*', line)
            
            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue
                    
                if is_passive_was_were_sentece(sentence):
                    total_sentences += 1
                    if page_index not in detected:
                        detected[page_index] = []
                    truncated_sentence = sentence[:50] + '...' if len(sentence) > 50 else sentence
                    if type == CritreriaType.PRESENTATION:
                        err_str = f'Строка {non_empty_line_counter}: {truncated_sentence}'
                    elif type == CritreriaType.REPORT:
                        err_str = f'Строка {line_index+1}: {truncated_sentence}'
                    detected[page_index].append(err_str)
                    
    return detected, total_sentences