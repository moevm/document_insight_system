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

_ = TranslationStringFactory('templater')
RECAPTCHA_ERROR='Recaptcha is not passed. Try to turn off VPN and / or  exit incognito mode.'

def recaptcha(request):
    ip = request.remote_addr
    token = request.POST['recaptcha-token']
    key = request.registry.settings['templater']['recaptcha_key']
    
    r = requests.post('https://www.google.com/recaptcha/api/siteverify', data={
        'secret': key,
        'response': token,
        'remoteip': ip
    })
    print("result of recaptcha request: {}".format(r.json()))

    return r.json()['score'] > 0.3


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
    if recaptcha(request):
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
    return HTTPBadRequest(body=json.dumps({'status': 'err', 'reason':RECAPTCHA_ERROR}))

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
    if recaptcha(request):
        try:
            template_id = request.POST['template-id']
            data_id = request.POST['data-table-id']

            template = request.fs.get(ObjectId(template_id))
            data = request.fs.get(ObjectId(data_id))

            renderer = TemplateRenderer()

            renderer.load_data(data)
            result = renderer.verify(template)

            # render messages from result['in_template] and result['in_csv]
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
    else: 
        return HTTPBadRequest(body=json.dumps({'status': 'err', 'reason':RECAPTCHA_ERROR}))

@view_config(route_name='render', request_method='POST', renderer='json')
def render_doc(request):
    if recaptcha(request):
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
    return HTTPBadRequest(body=json.dumps({'status': 'err', 'reason':RECAPTCHA_ERROR}))
