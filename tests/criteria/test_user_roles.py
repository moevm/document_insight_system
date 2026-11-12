"""Admin role editing through HTTP and targeted MongoDB updates."""

import runpy
import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest
from flask import Flask
from flask_login import LoginManager, UserMixin
from jinja2 import ChoiceLoader, DictLoader

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture
def role_app(monkeypatch):
    methods = ModuleType('app.db.methods.user')
    methods.get_user = Mock()
    methods.get_user_cursor = Mock(return_value=([], 0))
    methods.set_user_role = Mock(return_value=True)
    monkeypatch.setitem(sys.modules, methods.__name__, methods)
    routes = runpy.run_path(str(ROOT / 'app/routes/users.py'))

    class Account(UserMixin):
        username = 'admin'
        is_admin = True
        authenticated = True

    account = Account()
    app = Flask(__name__, template_folder=str(ROOT / 'app/templates'))
    app.secret_key = 'test-only-session-key'
    manager = LoginManager(app)
    manager.request_loader(lambda request: account if account.authenticated else None)
    app.register_blueprint(routes['users'], url_prefix='/users')
    app.add_url_rule('/checks', endpoint='check_list.check_list_main', view_func=lambda: '')
    app.jinja_loader = ChoiceLoader([DictLoader({'root.html': '{% block main %}{% endblock %}'}), app.jinja_loader])
    return app.test_client(), methods, account


@pytest.mark.parametrize('actor, expected', [('anonymous', 401), ('user', 403)])
def test_only_admin_can_set_roles(role_app, actor, expected):
    client, methods, account = role_app
    if actor == 'anonymous':
        account.authenticated = False
    account.is_admin = False
    response = client.put('/users/target/role', json={'is_admin': True})
    assert response.status_code == expected
    methods.set_user_role.assert_not_called()


@pytest.mark.parametrize('is_admin', [True, False])
def test_admin_can_promote_and_demote(role_app, is_admin):
    client, methods, _ = role_app
    response = client.put('/users/target/role', json={'is_admin': is_admin})
    assert response.status_code == 200
    assert response.get_json() == {'is_admin': is_admin}
    methods.set_user_role.assert_called_once_with('target', is_admin)


@pytest.mark.parametrize('data', [{}, None, [], 'admin', {'is_admin': 'false'}, {'is_admin': 1}, {'is_admin': None}])
def test_role_requires_json_boolean(role_app, data):
    client, methods, _ = role_app
    response = client.put('/users/target/role', json=data)
    assert response.status_code == 400
    methods.set_user_role.assert_not_called()


def test_form_cannot_change_role(role_app):
    client, methods, _ = role_app
    assert client.put('/users/target/role', data={'is_admin': 'true'}).status_code == 400
    methods.set_user_role.assert_not_called()


def test_unknown_user_returns_404(role_app):
    client, methods, _ = role_app
    methods.set_user_role.return_value = False
    assert client.put('/users/missing/role', json={'is_admin': True}).status_code == 404
    methods.get_user.return_value = None
    assert client.get('/users/missing').status_code == 404


def test_self_demotion_removes_access_to_user_management(role_app):
    client, methods, account = role_app

    def save_role(username, is_admin):
        assert username == account.username
        account.is_admin = is_admin
        return True

    methods.set_user_role.side_effect = save_role
    assert client.put('/users/admin/role', json={'is_admin': False}).status_code == 200
    assert client.get('/users/data').status_code == 403
    assert client.put('/users/target/role', json={'is_admin': True}).status_code == 403
    methods.set_user_role.assert_called_once_with('admin', False)


@pytest.mark.parametrize('is_admin, label', [(True, 'Администратор'), (False, 'Пользователь')])
def test_user_list_includes_role(role_app, is_admin, label):
    client, methods, _ = role_app
    methods.get_user_cursor.return_value = (
        [
            {
                'username': 'target',
                'name': 'Target',
                'formats': [],
                'criteria': 'Pack',
                'files': [],
                'is_admin': is_admin,
            }
        ],
        1,
    )
    assert client.get('/users/data').get_json()['rows'][0]['role'] == label


@pytest.mark.parametrize('is_lti', [True, False])
def test_role_form_shows_lti_behavior(role_app, is_lti):
    client, methods, _ = role_app
    methods.get_user.return_value = SimpleNamespace(username='target', is_admin=True, is_LTI=is_lti)
    response = client.get('/users/target')
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert 'data-url="/users/target/role"' in text
    assert '<option value="true" selected>' in text
    assert ('При следующем входе через LTI' in text) is is_lti


@pytest.mark.parametrize('matched_count', [0, 1])
def test_role_update_preserves_other_user_fields(monkeypatch, matched_count):
    collection = Mock()
    collection.update_one.return_value = SimpleNamespace(matched_count=matched_count, modified_count=0)
    db = ModuleType('app.db.db_main')
    db.get_users_collection = Mock(return_value=collection)
    monkeypatch.setitem(sys.modules, db.__name__, db)
    methods = runpy.run_path(str(ROOT / 'app/db/methods/user.py'))
    assert methods['set_user_role']('target', False) is bool(matched_count)
    collection.update_one.assert_called_once_with({'username': 'target'}, {'$set': {'is_admin': False}})
