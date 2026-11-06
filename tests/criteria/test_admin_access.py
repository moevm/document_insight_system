"""Exercise the merged admin guard without a MongoDB connection."""

import runpy
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
from flask import Flask
from flask_login import LoginManager, UserMixin


@pytest.mark.parametrize('role, expected_status', [('anonymous', 401), ('user', 403), ('admin', 200)])
def test_users_data_requires_authenticated_admin(monkeypatch, role, expected_status):
    user_methods = ModuleType('app.db.methods.user')
    user_methods.get_user = Mock()
    user_methods.get_user_cursor = Mock(return_value=([], 0))
    monkeypatch.setitem(sys.modules, 'app.db.methods.user', user_methods)
    route_path = Path(__file__).resolve().parents[2] / 'app' / 'routes' / 'users.py'
    routes = runpy.run_path(str(route_path))

    class User(UserMixin):
        id = role
        is_admin = role == 'admin'

    app = Flask(__name__)
    app.secret_key = 'test-only-session-key'
    manager = LoginManager(app)
    manager.request_loader(lambda request: None if role == 'anonymous' else User())
    app.register_blueprint(routes['users'], url_prefix='/users')

    response = app.test_client().get('/users/data')

    assert response.status_code == expected_status
    if role == 'admin':
        assert response.get_json() == {'total': 0, 'rows': []}
        user_methods.get_user_cursor.assert_called_once()
    else:
        user_methods.get_user_cursor.assert_not_called()
