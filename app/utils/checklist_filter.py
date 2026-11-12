import re

from bson import ObjectId
from flask_login import current_user

from .table_query import date_filter, number_filter, text_filter

FILTER_PREFIX = 'filter_'


def checklist_filter(data, is_admin=False):
    from utils import timezone_offset

    filters = {key[len(FILTER_PREFIX) :]: data[key] for key in data if key.startswith(FILTER_PREFIX)}
    query = {}
    for field in ('filename', 'user'):
        if value := filters.get(field):
            query[field] = text_filter(value)
    if criteria := filters.get('criteria'):
        query['criteria'] = {
            '$regex': '|'.join(re.escape(part.strip()) for part in criteria.split(',') if part.strip()),
            '$options': 'i',
        }
    if value := filters.get('upload-date'):
        query['_id'] = {
            operator: ObjectId.from_datetime(date) for operator, date in date_filter(value, timezone_offset).items()
        }
    if value := filters.get('moodle-date'):
        query['lms_passback_time'] = date_filter(value)
    if value := filters.get('score'):
        query['score'] = number_filter(value)
    status = filters.get('status')
    if status == 'processing':
        query['is_ended'] = False
    elif status in ('failed', 'passed', 'not-passed'):
        query['is_ended'] = {'$ne': False}
        query['is_failed'] = True if status == 'failed' else {'$ne': True}
        if status != 'failed':
            # Match the defaults used by Check for records without is_passed.
            passed = {'$or': [{'is_passed': True}, {'is_passed': {'$exists': False}, 'score': 1}]}
            query['$and'] = [passed if status == 'passed' else {'$nor': [passed]}]
    elif status:
        raise ValueError('Неизвестное состояние проверки.')
    if search := data.get('search', '').strip():
        query['$or'] = [{field: text_filter(search)} for field in ('filename', 'user', 'criteria')]
    if not (is_admin or current_user.is_admin):
        query['user'] = current_user.username
    return query
