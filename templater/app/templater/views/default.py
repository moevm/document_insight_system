from pyramid.view import view_config
from pyramid.response import Response
from pyramid.httpexceptions import HTTPFound,HTTPBadRequest
from pyramid.i18n import TranslationStringFactory
from pyramid.response import FileIter
from bson import ObjectId
from templater.lib.templater import RenderResult, TemplateRenderer
from tempfile import NamedTemporaryFile
import time
import urllib
import datetime
import requests
import json
import os
import tempfile
from .google_drive import (
    get_auth_url_and_flow, auth_flows,
    save_token, build_service,
    upload_file_to_drive, list_drive_folders
)
from googleapiclient.http import MediaFileUpload

import logging
log = logging.getLogger(__name__)



BASE_DIR = os.path.dirname(os.path.abspath(__file__))
JSON_FILE_PATH = os.path.join(BASE_DIR, '../data/templates.json')

@view_config(route_name='start_auth', renderer='json')
def start_auth(request):
    auth_url, state, flow = get_auth_url_and_flow()
    auth_flows[state] = flow
    return {'auth_url': auth_url}

@view_config(route_name='oauth_callback')
def oauth_callback(request):
    state = request.GET.get('state')
    code = request.GET.get('code')

    flow = auth_flows.pop(state, None)
    if not flow:
        return Response("Ошибка: неизвестный state", status=400)

    flow.fetch_token(code=code)
    creds = flow.credentials
    save_token(creds)

    return HTTPFound(location="/templates")

@view_config(route_name='export_template', request_method='POST', renderer='json')
def export_template(request):
    try:
        template_id = int(request.matchdict['template_id'])
        templates = load_templates()
        template = next((t for t in templates if t['id'] == template_id), None)
        if not template:
            return {'error': 'Шаблон не найден'}, 404

        folder_id = request.json_body.get("folder_id", None)

        service = build_service()

        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as temp_file:
            content = f"template_{template_id}"
            temp_file.write(content)
            temp_path = temp_file.name

        file_id = upload_file_to_drive(service, temp_path, f"template_{template_id}.txt", "text/plain", folder_id)
        os.unlink(temp_path)

        return {'message': 'Файл успешно экспортирован в Google Drive', 'file_id': file_id}
    except Exception as e:
        return {'error': str(e)}, 500

def load_templates():
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as file:
        return json.load(file)

def save_templates(templates):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as file:
        json.dump(templates, file, ensure_ascii=False, indent=4)

@view_config(route_name='templates', renderer='../templates/templates.jinja2')
def templates(request):
    templates_data = load_templates()
    return {'templates': templates_data}

@view_config(route_name='edit_template', renderer='../templates/edit_template.jinja2')
def edit_template(request):
    template_id = int(request.matchdict['template_id'])
    templates_data = load_templates()
    template = next((t for t in templates_data if t['id'] == template_id), None)
    if not template:
        return HTTPNotFound()

    if request.method == 'POST':
        template['name'] = request.POST.get('name')
        template['description'] = request.POST.get('description')
        save_templates(templates_data)
        return HTTPFound(location=request.route_url('templates'))

    return {'template': template}

@view_config(route_name='delete_template', request_method='POST')
def delete_template(request):
    template_id = int(request.matchdict['template_id'])
    templates_data = load_templates()
    templates_data = [t for t in templates_data if t['id'] != template_id]
    save_templates(templates_data)
    response = Response(json.dumps({"message": "Шаблон успешно удален"}), content_type='application/json; charset=UTF-8')
    return response

@view_config(route_name='delete_templates', renderer='../templates/delete_templates.jinja2')
def delete_templates(request):
    templates_data = load_templates()

    if request.method == 'POST':
        try:
            request_data = request.json_body
            selected_templates = request_data.get('selected_templates', [])

            templates_data = [t for t in templates_data if str(t['id']) not in selected_templates]
            save_templates(templates_data)

            return Response(json.dumps({"message": "Шаблоны успешно удалены"}), content_type='application/json; charset=UTF-8')

        except Exception as e:
            return Response(json.dumps({"error": str(e)}), content_type='application/json; charset=UTF-8', status=500)

    return {'templates': templates_data}


@view_config(route_name='api_update_template', request_method='POST', renderer='json')
def api_update_template(request):
    template_id = int(request.matchdict['template_id'])
    templates_data = load_templates()
    template = next((t for t in templates_data if t['id'] == template_id), None)
    if not template:
        return {'error': 'Шаблон не найден'}, 404

    data = request.json_body
    template['name'] = data.get('name')
    template['description'] = data.get('description')
    save_templates(templates_data)
    return {'message': 'Шаблон успешно обновлен'}

@view_config(route_name='add_template', renderer='../templates/add_template.jinja2')
def add_template(request):
    return {}

@view_config(route_name='api_add_template', request_method='POST', renderer='json')
def api_add_template(request):
    try:
        data = request.json_body
        name = data.get('name')
        description = data.get('description')
        template_type = "docx"
        created_at = "2023-10-01"

        templates_data = load_templates()
        new_id = max(t['id'] for t in templates_data) + 1 if templates_data else 1

        new_template = {
            "id": new_id,
            "name": name,
            "type": template_type,
            "description": description,
            "created_at": created_at,
        }

        templates_data.append(new_template)
        save_templates(templates_data)
        return {'message': 'Шаблон успешно добавлен', 'template': new_template}
    except Exception as e:
        return {'error': str(e)}, 500

_ = TranslationStringFactory('templater')



@view_config(route_name='captcha', renderer='../templates/verify_captcha.jinja2')
def verify_captcha_view(request):
    if check_captcha_verified(request):
        return HTTPFound(location=request.route_url('home'))

    if request.method == 'POST':
        if verify_captcha(request):
            request.session['captcha_verified'] = True
            return HTTPFound(location=request.route_url('home'))
        else:
            request.session.flash('Ошибка CAPTCHA. Повторите попытку.', 'error')

    return {'captcha_site_key': 'ysc1_4e0yUQRwmclR0orDgIUDhWwW8bbpnoRF2tRWeoQU87aa91d6'}

def verify_captcha(request):
    token = request.POST.get('smart-token')

    if not token:
        log.warning("smart-token отсутствует в POST")
        return False

    payload = {
        "secret": "ysc2_4e0yUQRwmclR0orDgIUDTMQJdCK2rjYTR0X7pq6L2b84dbd4",
        "token": token
    }

    try:
        response = requests.post(
            "https://smartcaptcha.yandexcloud.net/validate",
            json=payload,
            headers={
                "Content-Type": "application/json",
                "User-Agent": "TemplaterApp/1.0"
            },
            timeout=10
        )

        log.debug(f"SmartCaptcha ответ: {response.status_code} {response.text}")

        if response.status_code == 403:
            log.error("403 Forbidden. Проверь: ключ, IP, активность капчи")
            return True

        response.raise_for_status()
        result = response.json()
        return result.get("status") == "ok"

    except Exception as e:
        log.error(f"Ошибка запроса к капче: {str(e)}")
        return True

def check_captcha_verified(request):
    return request.session.get('captcha_verified', False)






@view_config(route_name='home', renderer='../templates/homepage.jinja2')
def home_page(request):
    request.response.samesite = 'none'
    return {'project': 'Templater'}


@view_config(route_name='locale')
def set_locale_cookie(request):
    if request.GET['language']:
        language = request.GET['language']
        response = Response()
        response.set_cookie('_LOCALE_',
                            value=language,
                            max_age=31536000)  # max_age = year
    return HTTPFound(location=request.environ['HTTP_REFERER'],
                     headers=response.headers)


@view_config(route_name='upload', request_method='POST', renderer='json')
def upload_doc(request):
        file_id = request.fs.put(
            request.POST['file'].file, filename=request.POST['file'].filename)
        max_age = request.registry.settings['templater'][
            'file_max_age'] if request.registry.settings['templater']['file_max_age'] else 60
        delta = datetime.timedelta(minutes=int(max_age))
        res = {'status': 'OK', 'file_name': request.POST['file'].filename, 'file_id': str(
            file_id), 'expire_at': (datetime.datetime.utcnow() + delta).isoformat()}
        if 'table-preview' in request.POST:
            datafile = request.fs.get(ObjectId(file_id))
            renderer = TemplateRenderer()
            renderer.load_data(datafile)
            res['data'] = renderer.raw_table
        return res

@view_config(route_name='files', request_method='GET')
def get_doc(request):
    file_id = ObjectId(request.GET['file_id'])
    file = request.fs.get(file_id)

    response = request.response
    response.app_iter = FileIter(file)
    response.content_disposition = "attachment; filename*=UTF-8''%s" % urllib.parse.quote(
        file.name.encode('utf8'))
    response.content_type = "application/vnd.oasis.opendocument.text"
    return response


@view_config(route_name='verify', request_method='POST', renderer='json')
def verify_doc(request):
        try:
            template_id = request.POST['template-id']
            data_id = request.POST['data-table-id']

            template = request.fs.get(ObjectId(template_id))
            data = request.fs.get(ObjectId(data_id))

            renderer = TemplateRenderer()

            renderer.load_data(data)
            result = renderer.verify(template)

            messages = []
            for field in result['in_template']:
                s = _('${field} not defined in the template', mapping={'field': field})
                s = request.localizer.translate(s)
                messages.append(s)

            for field in result['in_csv']:
                s = _('${field} not defined in the csv', mapping={'field': field})
                s = request.localizer.translate(s)
                messages.append(s)

            if(len(messages) == 0):
                s = _('Verification done without warning')
                s = request.localizer.translate(s)
                messages.append(s)
            return {'status': 'OK', 'messages': messages, 'fields': renderer.fieldnames}
        except:
            return {'status': 'err'}


@view_config(route_name='render', request_method='POST', renderer='json')
def render_doc(request):

        try:
            template_id = request.POST['template-id']
            data_id = request.POST['data-table-id']
            name_pattern = request.POST['name-pattern'] if 'name-pattern' in request.POST else None

            template = request.fs.get(ObjectId(template_id))
            data = request.fs.get(ObjectId(data_id))

            renderer = TemplateRenderer()

            renderer.load_data(data)
            result = renderer.render(template, name_pattern)

            files_id = {}
            for filename in result.files:
                # tmp = NamedTemporaryFile()
                try:
                    tmp = request.fs.new_file(filename=filename)
                    tmp.write(result.files[filename].getvalue())
                finally:
                    tmp.close()
                    files_id[filename] = str(tmp._id)

            archive_id = None
            archive_name = None
            if(result.archive is not None):
                try:
                    archive_name = template.name.rsplit('.', 1)[0]+".zip"
                    tmp = request.fs.new_file(filename=archive_name)
                    tmp.write(result.archive.getvalue())
                finally:
                    tmp.close()
                    archive_id = str(tmp._id)

            return {'status': 'OK', 'files': files_id, 'archive': str(archive_id) if archive_id is not None else '', 'archive_name': archive_name}
        except:
            return {'status': 'err'}

@view_config(route_name='dis_redirect')
def dis_redirect(request):
    dis_url = os.environ.get("DIS_URL", "http://localhost:8080/")
    return HTTPFound(location=dis_url)

@view_config(route_name='input_template_data', renderer='../templates/input_data_template.jinja2')
def input_template_data_view(request):
    template_id = int(request.matchdict['template_id'])
    templates_data = load_templates()
    template = next((t for t in templates_data if t['id'] == template_id), None)
    if not template:
        return HTTPNotFound()

    return {'template': template}

@view_config(route_name='api_save_template_data', request_method='POST', renderer='json')
def api_save_template_data(request):
    try:
        template_id = int(request.matchdict['template_id'])
        data = request.json_body.get('data')
        if not data:
            return {'error': 'Данные не переданы'}, 400

        templates_data = load_templates()
        template = next((t for t in templates_data if t['id'] == template_id), None)
        if not template:
            return {'error': 'Шаблон не найден'}, 404

        template['data'] = data
        save_templates(templates_data)

        return {'message': 'Данные успешно сохранены'}
    except Exception as e:
        return {'error': str(e)}, 500


