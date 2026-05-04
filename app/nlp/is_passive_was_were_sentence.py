import re
import string

import pymorphy3

morph = pymorphy3.MorphAnalyzer()


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
    first_words = re.split(r"\s+", sentence.strip(), maxsplit=2)
    if len(first_words) < 2:
        return False

    first_word = clean_word(first_words[0])
    second_word = clean_word(first_words[1])

    parsed = morph.parse(first_word)[0]
    if parsed.normal_form == "быть" and "past" in parsed.tag and parsed.tag.POS == "VERB":
        second_word_parsed = morph.parse(second_word)[0]
        return "PRTS" in second_word_parsed.tag and "pssv" in second_word_parsed.tag
    return False


def clean_word(word):
    punct = string.punctuation.replace("-", "")
    return word.translate(str.maketrans("", "", punct))
