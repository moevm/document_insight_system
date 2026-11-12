"""Run real templates/bundles in headless Chrome against synthetic HTTP fixtures.

No MongoDB, Redis, user data or running DIS deployment is used.
Run after npm run build: .venv/bin/python tests/frontend/browser_smoke.py
"""

import argparse
import json
import re
import shutil
import subprocess
import tempfile
import threading
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace

from flask import Flask, Response, jsonify, render_template, request
from flask_login import LoginManager, UserMixin
from werkzeug.serving import WSGIRequestHandler, make_server

ROOT = Path(__file__).resolve().parents[2]
REQUESTS = []


class QuietHandler(WSGIRequestHandler):
    def log_request(self, *args, **kwargs):
        pass


class Admin(UserMixin):
    username = 'admin'
    name = 'Test admin'
    is_admin = True


def fixture_app():
    app = Flask(__name__, static_folder=str(ROOT / 'src'), template_folder=str(ROOT / 'app/templates'))
    app.secret_key = 'test-only-key'
    manager = LoginManager(app)
    manager.request_loader(lambda req: Admin())
    app.add_url_rule(
        '/users/<username>/role',
        endpoint='users.user_role',
        methods=['PUT'],
        view_func=lambda username: jsonify(is_admin=request.json['is_admin']),
    )
    app.add_url_rule('/checks/<_id>', endpoint='checks.checks_main', view_func=lambda _id: '')

    @app.route('/users/')
    def users():
        return render_template('user_list.html')

    @app.route('/users/student')
    def user():
        return render_template(
            'one_user_info.html', user_info=SimpleNamespace(username='student', is_admin=False, is_LTI=True)
        )

    @app.route('/check_list/', endpoint='check_list.check_list_main')
    def checks():
        return render_template('check_list.html')

    @app.route('/logs/')
    def logs():
        return render_template('logs.html')

    @app.route('/admin/criterions')
    def criteria():
        info = {
            'pres': {
                'criterion_pres': {
                    'label': 'Презентация',
                    'name': 'Pres',
                    'description': lambda _: 'Описание презентации',
                }
            },
            'report': {
                'criterion_report': {'label': 'Отчёт', 'name': 'Report', 'description': lambda _: 'Описание отчёта'}
            },
        }
        return render_template('admin_criterions.html', table_criteria=info)

    @app.route('/criterion_packs/')
    def packs():
        return render_template(
            'pack_list.html',
            packs=[
                {
                    'name': 'Pack',
                    'updated': datetime(2026, 11, 7),
                    'file_type': {'type': 'report', 'report_type': 'VKR'},
                }
            ],
        )

    app.add_url_rule('/criterion_pack/', endpoint='criterion_pack.criteria_pack_new', view_func=lambda: '')
    app.add_url_rule('/criterion_pack/<name>', endpoint='criterion_pack.criteria_pack', view_func=lambda name: '')

    @app.route('/results/test')
    def result():
        data = SimpleNamespace(
            is_ended=True,
            is_failed=False,
            correct=lambda: True,
            filename='fixture.docx',
            user='student',
            conv_pdf_fs_id=None,
            _id='test',
            enabled_checks=[{'name': 'Test criterion', 'score': 1, 'verdict': ['<b>Замечание</b>']}],
        )
        return render_template('results.html', results=data, columns=['ID', 'Пользователь'], stats=['test', 'student'])

    @app.route('/api/results/ready/<check_id>')
    def ready(check_id):
        return jsonify(is_ended=True)

    @app.route('/users/data')
    @app.route('/check_list/data')
    @app.route('/logs/data')
    def data():
        query = request.args.to_dict()
        REQUESTS.append({'path': request.path, 'query': query})
        search = query.get('search', '')
        if search == 'error':
            return jsonify(error='Тестовая ошибка загрузки'), 500
        filters = json.loads(query.get('filter', '{}'))
        if request.path == '/users/data':
            rows = [
                {
                    'username': f'user{i:02}',
                    'name': f'User {i}',
                    'role': 'Администратор' if i % 2 == 0 else 'Пользователь',
                    'is_LTI': i % 2 == 0,
                    'all_formats': ['docx', 'md'],
                    'all_criteria': 'Pack',
                    'check_counts': i,
                }
                for i in range(35)
            ]
            rows[0]['username'] = '<img src=x onerror="window.injected=1">'
            if filters.get('role'):
                rows = [row for row in rows if (row['role'] == 'Администратор') == (filters['role'] == 'admin')]
            if search:
                rows = [row for row in rows if search.lower() in row['name'].lower()]
        elif request.path == '/check_list/data':
            rows = [
                {
                    '_id': f'{i:024x}',
                    'filename': f'Work {i}.docx',
                    'criteria': 'Pack',
                    'user': 'student',
                    'lms-user-id': '-',
                    'upload-date': '07.11.2026 12:00:00',
                    'moodle-date': '-',
                    'score': 1,
                    'status': 'Пройдена',
                    'is_ended': True,
                    'is_passed': True,
                    'is_failed': False,
                }
                for i in range(35)
            ]
        else:
            rows = [
                {
                    'timestamp': '07.11.2026 12:00:00',
                    'check_id': 'test',
                    'stage': 'check',
                    'service-name': 'worker',
                    'levelname': 'ERROR',
                    'message': '<img src=x onerror="window.injected=1">',
                    'pathname': '/test/file.py',
                    'lineno': 1,
                }
            ]
        total = len(rows)
        offset, limit = int(query.get('offset', 0)), int(query.get('limit', 25))
        return jsonify(total=total, rows=rows[offset : offset + limit])

    @app.route('/get_csv/')
    @app.route('/get_zip/')
    def export():
        REQUESTS.append({'path': request.path, 'query': request.args.to_dict()})
        return Response('fixture', headers={'Content-Disposition': 'attachment'})

    @app.route('/test/requests')
    def requests():
        return jsonify(REQUESTS)

    @app.route('/browser-smoke')
    def smoke():
        return (
            '<!doctype html><meta charset="utf-8"><pre id="result">RUNNING</pre>'
            '<iframe style="width:100%;height:850px"></iframe><script>'
            + (ROOT / 'tests/frontend/browser_smoke.js').read_text()
            + '</script>'
        )

    return app


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--screenshots', type=Path, help='Directory for desktop/mobile previews')
    args = parser.parse_args()
    chrome = shutil.which('google-chrome') or shutil.which('chromium')
    if not chrome:
        raise SystemExit('Chrome/Chromium is required')
    server = make_server('127.0.0.1', 0, fixture_app(), threaded=True, request_handler=QuietHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        with tempfile.TemporaryDirectory(prefix='dis-table-browser-') as profile:
            result = subprocess.run(
                [
                    chrome,
                    '--headless',
                    '--disable-gpu',
                    '--disable-dev-shm-usage',
                    f'--user-data-dir={profile}',
                    '--dump-dom',
                    '--virtual-time-budget=30000',
                    '--window-size=1440,1000',
                    f'http://127.0.0.1:{server.server_port}/browser-smoke',
                ],
                capture_output=True,
                text=True,
                timeout=60,
            )
            report = re.search(r'<pre id="result">(.*?)</pre>', result.stdout, re.S)
            if result.returncode or not report or not report[1].startswith('ALL TABLE CHECKS PASSED'):
                Path('/tmp/dis-table-browser-dom.html').write_text(result.stdout)
                print(report[1] if report else 'No browser report')
                print(result.stderr[-2000:])
                raise SystemExit('Browser checks failed; inspect /tmp/dis-table-browser-dom.html')
            print(
                'ALL TABLE CHECKS PASSED: users, filters, URL, pagination, reset, errors, escaping, '
                'statistics, export, catalog, packs, logs and result details'
            )
            if args.screenshots:
                args.screenshots.mkdir(parents=True, exist_ok=True)
                for label, size in [('desktop', '1440,1000'), ('mobile', '390,844')]:
                    screenshot = args.screenshots.resolve() / f'tables-{label}.png'
                    preview = subprocess.run(
                        [
                            chrome,
                            '--headless',
                            '--disable-gpu',
                            '--disable-dev-shm-usage',
                            f'--user-data-dir={profile}',
                            f'--window-size={size}',
                            '--virtual-time-budget=3000',
                            f'--screenshot={screenshot}',
                            f'http://127.0.0.1:{server.server_port}/users/?limit=10&filter=%7B%22role%22%3A%22admin%22%7D',
                        ],
                        capture_output=True,
                        text=True,
                        timeout=30,
                    )
                    if preview.returncode or not screenshot.exists():
                        raise SystemExit(f'Screenshot failed: {preview.stderr[-1000:]}')
    finally:
        server.shutdown()


if __name__ == '__main__':
    main()
