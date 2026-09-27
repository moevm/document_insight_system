from datetime import datetime, timedelta

from bson import ObjectId

from app.db.methods.check import get_checks_cursor
from app.db.methods.user import get_user, get_user_cursor
from app.document_diff.service import ALLOWED_EXTENSIONS
from app.utils import checklist_filter, format_check_for_table


def comparison_filter(data, format_name):
    query = checklist_filter(data, is_admin=True)
    query['file_type.type'] = 'report' if format_name == 'docx' else 'pres'
    _add_student_filter(query, data.get('filter_student', '').strip())
    _add_id_and_date_filter(query, data.get('filter_id', '').strip(), data.get('filter_date_from', '').strip(), data.get('filter_date_to', '').strip())
    _add_score_filter(query, data.get('filter_score_from', '').strip(), data.get('filter_score_to', '').strip())
    return query


def _add_student_filter(query, student):
    if not student:
        return
    users, _ = get_user_cursor(filter={'$or': [{'name': {'$regex': student, '$options': 'i'}}, {'username': {'$regex': student, '$options': 'i'}}]}, limit=0)
    query['user'] = {'$in': [user['username'] for user in users]}


def _add_id_and_date_filter(query, document_id, date_from, date_to):
    if document_id and not all(character in '0123456789abcdefABCDEF' for character in document_id):
        raise ValueError('ID должен содержать только шестнадцатеричные символы')
    identifier = {'$regex': f'^{document_id}', '$options': 'i'} if document_id else None
    date_filter = {}
    try:
        if date_from:
            date_filter['$gte'] = ObjectId.from_datetime(datetime.fromisoformat(date_from))
        if date_to:
            date_filter['$lt'] = ObjectId.from_datetime(datetime.fromisoformat(date_to) + timedelta(seconds=1))
    except ValueError as error:
        raise ValueError('Укажите корректные дату и время') from error
    if identifier and date_filter:
        query['$and'] = [{'_id': identifier}, {'_id': date_filter}]
    elif identifier:
        query['_id'] = identifier
    elif date_filter:
        query['_id'] = date_filter


def _add_score_filter(query, score_from, score_to):
    if not score_from and not score_to:
        return
    try:
        score = ({'$gte': float(score_from)} if score_from else {}) | ({'$lte': float(score_to)} if score_to else {})
    except ValueError as error:
        raise ValueError('Укажите корректные значения баллов') from error
    if '$gte' in score and '$lte' in score and score['$gte'] > score['$lte']:
        raise ValueError('Начальный балл не может быть больше конечного')
    query['score'] = score


def documents(data, format_name):
    if format_name not in ALLOWED_EXTENSIONS:
        raise ValueError('Выберите поддерживаемый формат сравнения')
    rows, _ = get_checks_cursor(filter=comparison_filter(data, format_name), limit=100, sort='_id', order='desc')
    return [document_row(row) for row in rows]


def document_row(check):
    row = format_check_for_table(check)
    user = get_user(check['user'])
    row['student'] = user.name if user and user.name else check['user']
    return row


def student_suggestions(value):
    if len(value) < 2:
        return []
    users, _ = get_user_cursor(filter={'$or': [{'name': {'$regex': value, '$options': 'i'}}, {'username': {'$regex': value, '$options': 'i'}}]}, limit=10)
    return list(dict.fromkeys(user.get('name') or user['username'] for user in users))
