"""Table filtering, date boundaries and aggregation contracts without MongoDB."""

import runpy
import sys
from copy import deepcopy
from datetime import datetime, timedelta
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
from flask import Flask
from flask_login import LoginManager, UserMixin

from app.utils.checklist_filter import checklist_filter
from app.utils.table_query import date_filter, number_filter, page_options, read_filters

ROOT = Path(__file__).resolve().parents[2]


@pytest.mark.parametrize(
    'value, expected',
    [
        ('5', 5),
        ('> 5', {'$gt': 5}),
        ('>=5', {'$gte': 5}),
        ('<10', {'$lt': 10}),
        ('<=10', {'$lte': 10}),
        ('5-10', {'$gte': 5, '$lte': 10}),
    ],
)
def test_integer_conditions(value, expected):
    assert number_filter(value, integer=True) == expected


@pytest.mark.parametrize('value', ['>', '5x', '10-5', '1.5', '-2'])
def test_invalid_count_filter(value):
    with pytest.raises(ValueError):
        number_filter(value, integer=True)


def test_score_accepts_comma_and_range():
    assert number_filter('0,5-1') == {'$gte': 0.5, '$lte': 1}
    assert number_filter('-1') == -1


def test_date_range_includes_entire_last_day():
    shift = timedelta(hours=3)
    assert date_filter('01.11.2026-07.11.2026', shift) == {
        '$gte': datetime(2026, 10, 31, 21),
        '$lt': datetime(2026, 11, 7, 21),
    }
    assert date_filter('07.11.2026')['$lt'] == datetime(2026, 11, 8)
    with pytest.raises(ValueError):
        date_filter('08.11.2026-07.11.2026')


@pytest.mark.parametrize('value', ['[]', 'null', '"x"', '{"name": 1}', '{'])
def test_invalid_json_filters(value):
    with pytest.raises(ValueError):
        read_filters({'filter': value})


@pytest.mark.parametrize(
    'query', [{'limit': '0'}, {'limit': '101'}, {'offset': '-1'}, {'sort': '$where'}, {'order': 'a'}, {'limit': 'NaN'}]
)
def test_invalid_table_options(query):
    with pytest.raises(ValueError):
        page_options(query, {'username'}, 'username')


def test_non_admin_cannot_use_search_to_read_other_users():
    class User(UserMixin):
        username = 'me'
        is_admin = False

    app = Flask(__name__)
    manager = LoginManager(app)
    manager.request_loader(lambda request: User())
    with app.test_request_context('/'):
        query = checklist_filter({'filter_user': 'other', 'search': '.*', 'filter_score': '0.5-1'})
    assert query['user'] == 'me'
    assert query['$or'][0] == {'filename': {'$regex': r'\.\*', '$options': 'i'}}
    assert query['score'] == {'$gte': 0.5, '$lte': 1}


def load_check_methods(monkeypatch, collection):
    db = ModuleType('app.db.db_main')
    for name in ['get_checks_collection', 'get_files_info_collection', 'get_users_collection']:
        setattr(db, name, Mock(return_value=collection))
    monkeypatch.setitem(sys.modules, db.__name__, db)
    client = ModuleType('app.db.methods.client')
    client.get_db = Mock(return_value=Mock())
    monkeypatch.setitem(sys.modules, client.__name__, client)
    return runpy.run_path(str(ROOT / 'app/db/methods/check.py'))


def test_latest_checks_paginate_sort_count_and_preserve_filter(monkeypatch):
    collection = Mock()
    collection.aggregate.return_value = iter([{'rows': [{'user': 'b'}], 'count': [{'total': 40}]}])
    methods = load_check_methods(monkeypatch, collection)
    query = {'user': {'$regex': 'student'}}
    original = deepcopy(query)
    rows, count = methods['get_latest_check_cursor'](query, limit=10, offset=20, sort='moodle-date', order='asc')
    assert rows == [{'user': 'b'}] and count == 40
    assert query == original
    pipeline = collection.aggregate.call_args.args[0]
    assert pipeline[:3] == [
        {'$match': query},
        {'$sort': {'_id': -1}},
        {'$group': {'_id': '$user', 'check': {'$first': '$$ROOT'}}},
    ]
    assert pipeline[-1]['$facet']['rows'] == [
        {'$sort': {'lms_passback_time': 1, '_id': -1}},
        {'$skip': 20},
        {'$limit': 10},
    ]


def test_latest_export_is_unlimited(monkeypatch):
    collection = Mock()
    collection.aggregate.return_value = iter([])
    methods = load_check_methods(monkeypatch, collection)
    assert methods['get_checks'](latest=True, limit=0, offset=0) == ([], 0)
    assert not any('$limit' in step or '$facet' in step for step in collection.aggregate.call_args.args[0])


def test_user_sort_aliases_and_check_count(monkeypatch):
    collection = Mock()
    collection.count_documents.return_value = 3
    db = ModuleType('app.db.db_main')
    db.get_users_collection = Mock(return_value=collection)
    monkeypatch.setitem(sys.modules, db.__name__, db)
    methods = runpy.run_path(str(ROOT / 'app/db/methods/user.py'))
    methods['get_user_cursor'](sort='all_criteria', order='desc')
    collection.find.return_value.sort.assert_called_with([('criteria', -1), ('_id', 1)])
    methods['get_user_cursor'](limit=10, offset=10, sort='check_counts', order='asc')
    pipeline = collection.aggregate.call_args.args[0]
    assert pipeline[1] == {'$addFields': {'_check_count': {'$size': {'$ifNull': ['$files', []]}}}}
    assert pipeline[-2:] == [{'$skip': 10}, {'$limit': 10}]


def test_export_rows_keep_their_existing_fields():
    from bson import ObjectId

    from app.utils.formatters import format_check_for_table

    row = {'_id': ObjectId(), 'filename': 'x.md', 'criteria': 'Pack', 'user': 'me', 'score': 1}
    assert 'status' not in format_check_for_table(row)
    assert format_check_for_table(row, include_status=True)['status'] == 'Пройдена'
    assert format_check_for_table({**row, 'is_ended': False}, include_status=True)['status'] == 'В обработке'
    assert format_check_for_table({**row, 'is_failed': True}, include_status=True)['status'] == 'Ошибка'


@pytest.fixture
def checks_client(monkeypatch):
    import app.db.methods as db_methods

    checks = ModuleType('app.db.methods.check')
    checks.get_checks_cursor = Mock(return_value=([], 0))
    checks.get_latest_check_cursor = Mock(return_value=([], 0))
    monkeypatch.setitem(sys.modules, checks.__name__, checks)
    monkeypatch.setattr(db_methods, 'check', checks, raising=False)
    routes = runpy.run_path(str(ROOT / 'app/routes/check_list.py'))

    class User(UserMixin):
        username = 'me'
        name = 'Me'
        is_admin = False

    app = Flask(__name__)
    manager = LoginManager(app)
    manager.request_loader(lambda request: User())
    app.register_blueprint(routes['check_list'], url_prefix='/check_list')
    return app.test_client(), checks


def test_statistics_keeps_owner_restriction_with_search_and_latest(checks_client):
    client, checks = checks_client
    response = client.get(
        '/check_list/data',
        query_string={
            'filter_user': 'other',
            'search': 'x',
            'latest': '1',
            'limit': '10',
            'offset': '20',
            'sort': 'upload-date',
        },
    )
    assert response.status_code == 200
    options = checks.get_latest_check_cursor.call_args.kwargs
    assert options['filter']['user'] == 'me'
    assert options['sort'] == '_id' and options['limit'] == 10 and options['offset'] == 20
    checks.get_checks_cursor.assert_not_called()


@pytest.mark.parametrize(
    'query',
    [
        {'filter_upload-date': '31.02.2026'},
        {'filter_score': 'NaN'},
        {'filter_status': 'unknown'},
        {'sort': 'secret'},
        {'limit': '0'},
    ],
)
def test_invalid_statistics_filters_return_400(checks_client, query):
    client, checks = checks_client
    response = client.get('/check_list/data', query_string=query)
    assert response.status_code == 400
    assert response.get_json()['error']
    checks.get_checks_cursor.assert_not_called()
    checks.get_latest_check_cursor.assert_not_called()


@pytest.fixture
def users_table_client(monkeypatch):
    methods = ModuleType('app.db.methods.user')
    methods.get_user = Mock()
    methods.get_user_cursor = Mock(return_value=([], 0))
    methods.set_user_role = Mock()
    monkeypatch.setitem(sys.modules, methods.__name__, methods)
    routes = runpy.run_path(str(ROOT / 'app/routes/users.py'))

    class Admin(UserMixin):
        username = 'admin'
        is_admin = True

    app = Flask(__name__)
    manager = LoginManager(app)
    manager.request_loader(lambda request: Admin())
    app.register_blueprint(routes['users'], url_prefix='/users')
    return app.test_client(), methods


@pytest.mark.parametrize(
    'filters, expected',
    [
        ({'role': 'admin'}, {'is_admin': True}),
        ({'role': 'user'}, {'is_admin': {'$ne': True}}),
        ({'is_LTI': 'false'}, {'is_LTI': {'$ne': True}}),
        ({'all_formats': 'docx'}, {'formats': 'docx'}),
        ({'name': '[test]'}, {'name': {'$regex': r'\[test\]', '$options': 'i'}}),
    ],
)
def test_user_filters_target_database_fields(users_table_client, filters, expected):
    import json

    client, methods = users_table_client
    response = client.get('/users/data', query_string={'filter': json.dumps(filters)})
    assert response.status_code == 200
    assert methods.get_user_cursor.call_args.kwargs['filter'] == expected


def test_count_filter_and_pagination(users_table_client):
    client, methods = users_table_client
    response = client.get(
        '/users/data',
        query_string={
            'filter': '{"check_counts": "> 5"}',
            'sort': 'check_counts',
            'order': 'desc',
            'limit': '10',
            'offset': '20',
        },
    )
    assert response.status_code == 200
    assert methods.get_user_cursor.call_args.kwargs == {
        'filter': {'$expr': {'$and': [{'$gt': [{'$size': {'$ifNull': ['$files', []]}}, 5]}]}},
        'sort': 'check_counts',
        'order': 'desc',
        'limit': 10,
        'offset': 20,
    }


@pytest.mark.parametrize(
    'query',
    [
        {'filter': '[]'},
        {'filter': '{"role": "owner"}'},
        {'filter': '{"check_counts": ">"}'},
        {'sort': 'password_hash'},
        {'limit': '100000'},
    ],
)
def test_invalid_table_request_does_not_query_users(users_table_client, query):
    client, methods = users_table_client
    assert client.get('/users/data', query_string=query).status_code == 400
    methods.get_user_cursor.assert_not_called()
