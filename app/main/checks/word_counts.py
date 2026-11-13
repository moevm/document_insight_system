import re

from .base_check import morph


def normalize_phrase(text):
    return ' '.join(morph.normal_forms(word)[0] for word in re.findall(r'\w+(?:-\w+)*', text.lower()))


def phrase_counts(text, phrases):
    normalized = normalize_phrase(text)
    return {
        phrase: len(re.findall(r'(?<!\w)' + re.escape(phrase) + r'(?!\w)', normalized)) for phrase in phrases if phrase
    }
