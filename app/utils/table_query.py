"""Parsing shared by the server-backed tables; no database access."""

import json
import re
from datetime import datetime, timedelta


def read_filters(args):
    try:
        filters = json.loads(args.get('filter') or '{}')
    except (TypeError, ValueError) as error:
        raise ValueError('Фильтры должны быть JSON-объектом.') from error
    if not isinstance(filters, dict) or any(not isinstance(value, str) for value in filters.values()):
        raise ValueError('Значения фильтров должны быть строками.')
    return filters


def page_options(args, sorts, default_sort, default_order='asc'):
    try:
        limit = int(args.get('limit', 10))
        offset = int(args.get('offset', 0))
    except (TypeError, ValueError) as error:
        raise ValueError('Неверный размер страницы или смещение.') from error
    if not 1 <= limit <= 100 or offset < 0:
        raise ValueError('Размер страницы должен быть от 1 до 100, смещение — неотрицательным.')
    sort = args.get('sort') or default_sort
    order = args.get('order') or default_order
    if sort not in sorts or order not in ('asc', 'desc'):
        raise ValueError('Неверное поле или направление сортировки.')
    return {'limit': limit, 'offset': offset, 'sort': sort, 'order': order}


def text_filter(value):
    return {'$regex': re.escape(value), '$options': 'i'}


def number_filter(value, integer=False):
    number = r'\d+' if integer else r'-?\d+(?:[.,]\d+)?'
    parse = int if integer else lambda text: float(text.replace(',', '.'))
    if match := re.fullmatch(rf'\s*(>=|<=|>|<|=)?\s*({number})\s*', value):
        operator, operand = match.groups()
        operand = parse(operand)
        return (
            operand
            if not operator or operator == '='
            else {{'>': '$gt', '>=': '$gte', '<': '$lt', '<=': '$lte'}[operator]: operand}
        )
    if match := re.fullmatch(rf'\s*({number})\s*-\s*({number})\s*', value):
        start, end = map(parse, match.groups())
        if start <= end:
            return {'$gte': start, '$lte': end}
    raise ValueError('Числовой фильтр: укажите число, сравнение (>= 5) или диапазон (5-10).')


DATE_FORMAT = '%d.%m.%Y'
DATE_TIME_FORMAT = '%d.%m.%Y %H:%M'
TIME_FORMAT = '%H:%M'


def parse_moment(text):
    """Return (datetime, has_time) for 'ДД.ММ.ГГГГ' or 'ДД.ММ.ГГГГ ЧЧ:ММ'."""
    text = text.strip()
    for fmt in (DATE_TIME_FORMAT, DATE_FORMAT):
        try:
            return datetime.strptime(text, fmt), fmt == DATE_TIME_FORMAT
        except ValueError:
            continue
    raise ValueError


def date_boundaries(value):
    text = value.replace('\u2013', '-').strip()
    try:
        start_text, _, end_text = text.partition('-')
        start, start_has_time = parse_moment(start_text)
        if not end_text.strip():
            return start, start + (timedelta(minutes=1) if start_has_time else timedelta(days=1))
        try:
            end, end_has_time = parse_moment(end_text)
        except ValueError:
            clock = datetime.strptime(end_text.strip(), TIME_FORMAT)
            end = start.replace(hour=clock.hour, minute=clock.minute, second=0, microsecond=0)
            end_has_time = True
        if not end_has_time:
            end += timedelta(days=1)
        if end <= start:
            raise ValueError
    except (ValueError, OverflowError) as error:
        raise ValueError(
            'Дата: укажите ДД.ММ.ГГГГ или ДД.ММ.ГГГГ ЧЧ:ММ, диапазон — через дефис, '
            'например 24.11.2026 12:00-25.11.2026 13:00. Время без даты не поддерживается.'
        ) from error
    return start, end


def date_filter(value, shift=timedelta()):
    start, end = date_boundaries(value)
    return {'$gte': start - shift, '$lt': end - shift}
