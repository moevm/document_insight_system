import json
import time
import uuid
from os.path import join

from bson import ObjectId
from celery import chord
from flask import abort, request
from flask_login import current_user

from app.db.methods import document_diff as comparison_methods
from app.db.methods.check import get_check
from app.server_consts import UPLOAD_FOLDER
from app.tasks import convert_check_file_to_pdf, compare_documents
from app.utils.check_file import check_file

ALLOWED_EXTENSIONS = {'docx': {'doc', 'docx', 'md', 'odt'}, 'pptx': {'ppt', 'pptx', 'odp'}}


def meta_path(comparison_id):
    return join(UPLOAD_FOLDER, f'{comparison_id}.json')


def read_meta(comparison_id):
    try:
        with open(meta_path(comparison_id), encoding='utf-8') as file:
            return json.load(file)
    except (FileNotFoundError, ValueError):
        abort(404)


def write_meta(comparison_id, meta):
    with open(meta_path(comparison_id), 'w', encoding='utf-8') as file:
        json.dump(meta, file)


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
    return {'extension': extension, 'filename': uploaded_file.filename, 'pdf_id': str(ObjectId())}


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
    conversions = []
    for number, source in enumerate(sources, 1):
        if source.get('pdf_id'):
            path = join(UPLOAD_FOLDER, f'{comparison_id}_{number}.{source["extension"]}')
            conversions.append(
                convert_check_file_to_pdf.s({'filename': source['filename'], 'conv_pdf_fs_id': source['pdf_id']}, path)
            )
    callback = compare_documents.si(comparison_id, format_name, *sources)
    return chord(conversions)(callback) if conversions else callback.delay()


def create_comparison(format_name, form=None, files=None):
    comparison_id = uuid.uuid4().hex
    sources = [source_for(side, comparison_id, format_name, form, files) for side in ('first', 'second')]
    task = _start_task(comparison_id, format_name, sources)
    comparison_record_id = comparison_methods.add_comparison(
        {
            'comparison_id': comparison_id,
            'username': current_user.username,
            'format': format_name,
            'first_source': sources[0],
            'second_source': sources[1],
            'task_id': task.id,
            'status': 'pending',
            'created_at': time.time(),
        }
    )
    write_meta(
        comparison_id,
        {
            'username': current_user.username,
            'fmt': format_name,
            'first_filename': sources[0]['filename'],
            'second_filename': sources[1]['filename'],
            'task_id': task.id,
            'comparison_record_id': str(comparison_record_id),
        },
    )
    return comparison_id
