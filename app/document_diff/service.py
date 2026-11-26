import time
from os.path import join

from bson import ObjectId
from flask import abort, request
from flask_login import current_user

from app.db.methods import document_diff as comparison_methods
from app.db.methods.check import get_check
from app.document_diff.tasks import compare_documents
from app.server_consts import UPLOAD_FOLDER
from app.utils.check_file import check_file

ALLOWED_EXTENSIONS = {'docx': {'doc', 'docx', 'md', 'odt'}, 'pptx': {'ppt', 'pptx', 'odp'}}


def read_meta(comparison_id):
    try:
        meta = comparison_methods.get_comparison(ObjectId(comparison_id))
    except Exception:
        abort(404)
    if meta is None:
        abort(404)
    return meta


def write_meta(comparison_id, meta):
    comparison_record_id = meta.get('_id')
    if comparison_record_id is None:
        try:
            comparison = comparison_methods.get_comparison(ObjectId(comparison_id))
        except Exception:
            abort(404)
        if comparison is None:
            abort(404)
        comparison_record_id = comparison['_id']
    values = {key: value for key, value in meta.items() if key != '_id'}
    comparison_methods.update_comparison(comparison_record_id, values)


def _system_source(document_id, format_name):
    check = get_check(ObjectId(document_id))
    if check is None:
        raise ValueError('Документ не найден в системе')
    file_type = 'report' if format_name == 'docx' else 'pres'
    if check.file_type.get('type') != file_type:
        expected = 'документ' if format_name == 'docx' else 'презентацию'
        raise ValueError(f'Выбранный файл не подходит для сравнения: нужно выбрать {expected}')
    extension = check.filename.rsplit('.', 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS[format_name]:
        raise ValueError('Формат файла не является допустимым для выбранного типа сравнения')
    return {'check_id': str(check._id), 'extension': extension, 'filename': check.filename}


def _uploaded_source(side, comparison_id, format_name, uploaded_file):
    if '.' not in uploaded_file.filename:
        raise ValueError('У файла должно быть расширение')
    extension = uploaded_file.filename.rsplit('.', 1)[-1].lower()
    if extension not in ALLOWED_EXTENSIONS[format_name] or check_file(
        uploaded_file, extension, ALLOWED_EXTENSIONS[format_name], check_mime=extension != 'md'
    ):
        raise ValueError('Выбран неподдерживаемый формат файла')
    number = 1 if side == 'first' else 2
    uploaded_file.save(join(UPLOAD_FOLDER, f'{comparison_id}_{number}.{extension}'))
    return {'extension': extension, 'filename': uploaded_file.filename}


def source_for(side, comparison_id, format_name, form=None, files=None):
    form = request.form if form is None else form
    files = request.files if files is None else files
    document_id = form.get(f'{side}_document_id', '')
    uploaded_file = files.get(f'{side}_file')
    if document_id:
        return _system_source(document_id, format_name)
    if uploaded_file and uploaded_file.filename:
        return _uploaded_source(side, comparison_id, format_name, uploaded_file)
    raise ValueError('Выберите документ для сравнения')


def _start_task(comparison_id, format_name, sources):
    return compare_documents.delay(comparison_id, format_name, *sources)


def create_comparison(format_name, form=None, files=None):
    comparison_record_id = ObjectId()
    comparison_id = str(comparison_record_id)
    sources = [source_for(side, comparison_id, format_name, form, files) for side in ('first', 'second')]
    comparison_methods.add_comparison(
        {
            '_id': comparison_record_id,
            'username': current_user.username,
            'format': format_name,
            'fmt': format_name,
            'first_source': sources[0],
            'second_source': sources[1],
            'first_filename': sources[0]['filename'],
            'second_filename': sources[1]['filename'],
            'task_id': None,
            'status': 'pending',
            'created_at': time.time(),
        }
    )
    task = _start_task(comparison_id, format_name, sources)
    comparison_methods.update_comparison(comparison_record_id, {'task_id': task.id})
    return comparison_id
