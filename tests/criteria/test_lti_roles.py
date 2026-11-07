"""Check LTI role synchronization without MongoDB or an external LMS."""

import runpy
import sys
from pathlib import Path
from types import ModuleType
from unittest.mock import Mock

import pytest
from flask import Flask
from flask_login import LoginManager, current_user

from app.db.types.User import User


@pytest.fixture
def lti_routes(monkeypatch):
    root = Path(__file__).resolve().parents[2]
    validator = ModuleType('app.lti_session_passback.lti.check_request')
    validator.check_request = Mock(return_value=True)
    monkeypatch.setitem(sys.modules, validator.__name__, validator)
    logger = ModuleType('app.root_logger')
    logger.get_root_logger = Mock(return_value=Mock())
    monkeypatch.setitem(sys.modules, logger.__name__, logger)

    import app.db.methods as db_methods
    import app.lti_session_passback.lti as lti_package

    utils = ModuleType('app.lti_session_passback.lti.utils')
    utils.__dict__.update(runpy.run_path(str(root / 'app/lti_session_passback/lti/utils.py')))
    monkeypatch.setattr(lti_package, 'utils', utils, raising=False)
    monkeypatch.setitem(sys.modules, 'app.lti_session_passback.lti.utils', utils)

    users = ModuleType('app.db.methods.user')
    users.add_user = Mock()
    users.get_user = Mock()
    packs = ModuleType('app.db.methods.criteria_pack')
    packs.get_criteria_pack = Mock(return_value={'raw_criterions': [], 'file_type': {'type': 'pres'}})
    editing = ModuleType('app.db.methods.edit_user')
    editing.edit_user = Mock(return_value=True)
    for name, module in [('user', users), ('criteria_pack', packs), ('edit_user', editing)]:
        monkeypatch.setitem(sys.modules, f'app.db.methods.{name}', module)
        monkeypatch.setattr(db_methods, name, module, raising=False)

    routes = runpy.run_path(str(root / 'app/routes/lti.py'))
    app = Flask(__name__)
    app.secret_key = 'test-only-session-key'
    manager = LoginManager(app)
    manager.user_loader(lambda username: users.get_user(username))
    app.add_url_rule('/upload/', endpoint='upload.upload_main', view_func=lambda: 'upload')
    app.add_url_rule('/session-role', view_func=lambda: {'is_admin': current_user.is_admin})
    app.register_blueprint(routes['lti'], url_prefix='/lti')
    return app.test_client(), users, editing.edit_user, validator.check_request, utils


@pytest.mark.parametrize(
    'roles, expected',
    [
        ('Learner', False),
        ('Instructor', True),
        ('Learner,Instructor', True),
        ('Instructor,Learner', True),
        ('Learner, Instructor ', True),
        ('TeachingAssistant', False),
        ('NotInstructor', False),
        ('', False),
        (None, False),
    ],
)
def test_instructor_role_is_exact_and_independent_of_order(lti_routes, roles, expected):
    utils = lti_routes[-1]
    data = {} if roles is None else {'roles': roles}
    assert utils.get_role(data) is expected


@pytest.mark.parametrize('new_user', [False, True])
def test_lti_launch_synchronizes_role_on_every_login(lti_routes, new_user):
    client, users, save, validate, _ = lti_routes
    user = User({'username': 'student_lms', 'is_LTI': True})
    users.add_user.side_effect = [user if new_user else None, None, None]
    users.get_user.return_value = user
    payload = {
        'ext_user_username': 'student',
        'tool_consumer_instance_guid': 'lms',
        'lis_person_name_full': 'Test User',
        'user_id': 'lms-user',
        'lis_outcome_service_url': 'https://lms.example/outcome',
        'lis_result_sourcedid': 'result',
        'oauth_consumer_key': 'test-consumer',
    }
    saved_roles = []
    save.side_effect = lambda saved_user: saved_roles.append(saved_user.is_admin) or True

    for roles, expected in [('Learner', False), ('Learner,Instructor', True), ('Learner', False)]:
        response = client.post('/lti/', data={**payload, 'roles': roles})
        assert response.status_code == 302
        assert user.is_admin is expected
        assert client.get('/session-role').get_json() == {'is_admin': expected}

    assert saved_roles == [False, True, False]
    assert validate.call_count == 3
    assert users.add_user.call_count == 3
    assert all(call.args == ('student_lms',) for call in users.add_user.call_args_list)


def test_rejected_lti_launch_does_not_change_role(lti_routes):
    client, users, save, validate, _ = lti_routes
    validate.return_value = False
    response = client.post('/lti/', data={'roles': 'Instructor'})
    assert response.status_code == 403
    users.add_user.assert_not_called()
    users.get_user.assert_not_called()
    save.assert_not_called()
