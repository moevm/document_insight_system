import re
from pymorphy3 import MorphAnalyzer
import json
from pathlib import Path

morph = MorphAnalyzer()

DEBUG_MODE = False


def load_abbreviations():
    config_path = config_path = (
        Path(__file__).parent.parent / "configs" / "config_abbreviations.json"
    )
    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return set(data.get("common_abbr"))


COMMON_ABBR = load_abbreviations()


def debug_print(*args, **kwargs):
    if DEBUG_MODE:
        print(*args, **kwargs)


def get_first_letters(phrase):
    if not phrase:
        return ""
    words = phrase.split()
    return "".join(word[0].upper() for word in words if word)


def is_abbreviation_explained(abbr: str, text: str) -> bool:
    patterns = [
        rf"{abbr}\s*\(([^)]+)\)",  # АААА (расшифровка)
        rf"\(([^)]+)\)\s*{abbr}",  # (расшифровка) АААА
        rf"{abbr}\s*[—\-]\s*([^.,;!?]+)",  # АААА — расшифровка
        rf"{abbr}\s*-\s*([^.,;!?]+)",  # АААА - расшифровка
        rf"([^.,;!?]+)\s*[—\-]\s*{abbr}",  # расшифровка — АААА
        rf"([^.,;!?]+)\s*-\s*{abbr}",  # расшифровка - АААА
    ]

    debug_print(f"Проверка аббревиатуры: {abbr}")
    debug_print(f"Текст (первые 200 символов): {text[:200]}...")

    for pattern in patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            explanation = match.group(1)
            debug_print(f" Найден паттерн {pattern}")
            debug_print(f"  Расшифровка: {explanation}")

            if correctly_explained(abbr, explanation):
                debug_print(f"  Расшифровка корректна")
                return True
            else:
                debug_print(f"  Расшифровка НЕ соответствует первым буквам")
                debug_print(f"     Ожидалось: {abbr.upper()}")
                debug_print(f"     Получено: {get_first_letters(explanation)}")

    debug_print(f" Расшифровка для {abbr} не найдена")
    return False


def get_unexplained_abbrev(text, unverifiable_text):
    abbreviations = find_abbreviations(text, unverifiable_text)

    if not abbreviations:
        return False, []

    unexplained_abbr = []
    for abbr in abbreviations:
        if not is_abbreviation_explained(abbr, text):
            unexplained_abbr.append(abbr)

    return True, unexplained_abbr


def find_abbreviations(text: str, unverifiable_text: str):
    pattern = r"\b[А-ЯA-Z]{2,5}\b"
    abbreviations = re.findall(pattern, text)

    filtered_abbr = {
        abbr
        for abbr in abbreviations
        if abbr not in COMMON_ABBR
        and abbr not in unverifiable_text
        and morph.parse(abbr.lower())[0].score != 0
    }

    return list(filtered_abbr)


def correctly_explained(abbr, explan):
    words = explan.split()

    first_letters = ""
    for word in words:
        if word:
            first_letters += word[0].upper()

    return first_letters == abbr.upper()


def main_check(text: str, unverifiable_text: str):
    try:
        debug_print(f"unverifiable_text : {unverifiable_text}")
        continue_check = True
        res_str = ""
        if not text:
            continue_check, res_str = False, "Не удалось получить текст"

        abbr_is_finding, unexplained_abbr = get_unexplained_abbrev(
            text=text, unverifiable_text=unverifiable_text
        )

        if not abbr_is_finding:
            continue_check, res_str = (
                False,
                "Аббревиатуры не найдены в представленном документе",
            )

        if not unexplained_abbr:
            continue_check, res_str = False, "Все аббревиатуры правильно расшифрованы"

        return continue_check, res_str, unexplained_abbr

    except Exception as e:
        return False, f"Ошибка при проверке аббревиатур: {str(e)}", {}


def forming_response(unexplained_abbr_with_page, format_page_link):
    result_str = "Найдены нерасшифрованные аббревиатуры при первом использовании:<br>"
    page_links = format_page_link(list(unexplained_abbr_with_page.values()))
    for index_links, abbr in enumerate(unexplained_abbr_with_page):
        result_str += f"- {abbr} на {page_links[index_links]} странице<br>"
    result_str += "Каждая аббревиатура должна быть расшифрована при первом использовании в тексте.<br>"
    result_str += "Расшифровка должны быть по первыми буквам, например, МВД - Министерство внутренних дел.<br>"
    return result_str
