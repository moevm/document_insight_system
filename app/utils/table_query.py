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


def date_filter(value, shift=timedelta()):
    try:
        parts = value.split('-')
        if not 1 <= len(parts) <= 2:
            raise ValueError
        start = datetime.strptime(parts[0].strip(), '%d.%m.%Y')
        end = datetime.strptime(parts[-1].strip(), '%d.%m.%Y')
        if end < start:
            raise ValueError
        return {'$gte': start - shift, '$lt': end + timedelta(days=1) - shift}
    except (ValueError, OverflowError) as error:
        raise ValueError('Дата: укажите ДД.ММ.ГГГГ или диапазон ДД.ММ.ГГГГ-ДД.ММ.ГГГГ.') from error
