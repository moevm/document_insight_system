import re
import pymorphy2
import string
from enum import Enum

morph = pymorphy2.MorphAnalyzer()


class CritreriaType(Enum):
    REPORT=0
    PRESENTATION=1


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


def generate_output_text(detected_senteces, type: CritreriaType):
    output = 'Обнаружены конструкции (Был/Была/Было/Были), которые можно удалить без потери смысла:<br><br>'
    for index, messages in detected_senteces.items():
        output_type = criteria_type_to_str(type)
        output += f'{output_type} №{index + 1}: <br>' + '<br>'.join(messages) + '<br><br>'
    return output


def get_was_were_sentences(file, type: CritreriaType):
    detected = {}
    total_sentences = 0
    for page_index, page_text in get_content_by_file(file, type):
        sentences = re.split(r'(?<=[.!?…])\s+', page_text)
        for sentence_index, sentence in enumerate(sentences):
            if is_passive_was_were_sentece(sentence):
                total_sentences += 1
                if page_index not in detected:
                    detected[page_index] = []
                truncated_sentence = sentence[:30] + '...' if len(sentence) > 30 else sentence
                detected[page_index].append(f'{sentence_index+1}: {truncated_sentence}')
    return detected, total_sentences