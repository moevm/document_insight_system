"""Deterministic Russian text helpers that do not download data at check time."""

import re

from pymorphy3 import MorphAnalyzer

_morph = MorphAnalyzer()
_SERVICE_POS = {'PREP', 'CONJ', 'PRCL', 'INTJ', 'NPRO'}


def word_tokens(text):
    return re.findall(r"\b\w+(?:[-']\w+)*\b", text.lower())


def content_lemmas(text):
    result = []
    for word in word_tokens(text):
        variants = _morph.parse(word)
        parsed = next(
            (variant for variant in variants if variant.tag.POS == 'NOUN' and variant.score >= 0.1), variants[0]
        )
        if parsed.tag.POS not in _SERVICE_POS:
            result.append(parsed.normal_form)
    return result


def sentence_tokens(text):
    from nltk.tokenize import PunktSentenceTokenizer, sent_tokenize

    try:
        return sent_tokenize(text, language='russian')
    except LookupError:
        return PunktSentenceTokenizer().tokenize(text)
