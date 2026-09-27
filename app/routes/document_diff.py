from bson import ObjectId
from celery.result import AsyncResult
from flask import Blueprint, abort, jsonify, redirect, render_template, request, send_from_directory, url_for
from flask_login import login_required

from app.db.methods import document_diff as comparison_methods
from app.document_diff.selection import documents, student_suggestions
from app.document_diff.service import ALLOWED_EXTENSIONS, UPLOAD_FOLDER, create_comparison, read_meta, write_meta
from app.routes.admin import admin_required

document_diff = Blueprint('document_diff', __name__, template_folder='templates', static_folder='static')


def _protected(view):
    return login_required(admin_required(view))


def _file_url(comparison_id, filename, download=False):
    return url_for(
        'document_diff.document_diff_file',
        comparison_id=comparison_id,
        filename=filename,
        download='1' if download else None,
    )


def _result_data(comparison_id, meta):
    if meta['fmt'] == 'docx':
        return {'format': 'docx', 'fragments': meta.get('fragments', [])}
    mapping = []
    for item in meta.get('mapping', []):
        item = item.copy()
        for field, side in (('slide_a', 'a'), ('slide_b', 'b')):
            if item.get(field) is not None:
                item[f'image_{side}'] = _file_url(comparison_id, f'{comparison_id}_{side}_slide_{item[field]}.png')
        mapping.append(item)
    return {'format': 'pptx', 'mapping': mapping}


def _render_result(comparison_id, meta):
    return render_template(
        'document_diff.html',
        navi_upload=True,
        fmt=meta['fmt'],
        data=_result_data(comparison_id, meta),
        stats=meta.get('stats'),
        first_filename=meta['first_filename'],
        second_filename=meta['second_filename'],
        first_pdf_url=_file_url(comparison_id, f'{comparison_id}_1_hl.pdf'),
        second_pdf_url=_file_url(comparison_id, f'{comparison_id}_2_hl.pdf'),
        diff_docx_url=_file_url(comparison_id, f'{comparison_id}_diff.docx', True),
        pdf_url=_file_url(comparison_id, f'{comparison_id}_diff_highlighted.pdf', True),
    )


@document_diff.route('/')
@_protected
def document_diff_select_page():
    return render_template('document_diff_select.html', navi_upload=True)


@document_diff.route('/data')
@_protected
def document_diff_data():
    try:
        return jsonify({'rows': documents(request.args, request.args.get('format', 'docx'))})
    except ValueError as error:
        return jsonify({'error': str(error)}), 400


@document_diff.route('/student-suggestions')
@_protected
def document_diff_student_suggestions():
    return jsonify({'items': student_suggestions(request.args.get('query', '').strip())})


@document_diff.route('/compare', methods=['POST'])
@_protected
def document_diff_compare():
    format_name = request.form.get('format', 'docx')
    if format_name not in ALLOWED_EXTENSIONS:
        return 'Выберите поддерживаемый формат сравнения', 400
    try:
        comparison_id = create_comparison(format_name)
    except ValueError as error:
        return render_template('document_diff_select.html', navi_upload=True, fmt=format_name, error=str(error)), 400
    return redirect(url_for('document_diff.document_diff_result', comparison_id=comparison_id))


@document_diff.route('/result/<string:comparison_id>')
@_protected
def document_diff_result(comparison_id):
    meta = read_meta(comparison_id)
    task = AsyncResult(meta['task_id'])
    if not task.ready():
        return render_template(
            'document_diff.html',
            navi_upload=True,
            pending=True,
            comparison_id=comparison_id,
            first_filename=meta['first_filename'],
            second_filename=meta['second_filename'],
        )
    if task.failed():
        record_id = meta.get('comparison_record_id') or meta.get('comparison_id')
        comparison_methods.update_comparison(ObjectId(record_id), {'status': 'error', 'error': str(task.result)})
        return render_template(
            'document_diff_select.html', navi_upload=True, fmt=meta['fmt'], error=str(task.result)
        ), 500
    meta.update(task.result)
    write_meta(comparison_id, meta)
    record_id = meta.get('comparison_record_id') or meta.get('comparison_id')
    comparison_methods.update_comparison(ObjectId(record_id), {'status': 'done', 'result': task.result})
    return _render_result(comparison_id, meta)


@document_diff.route('/status/<string:comparison_id>')
@_protected
def document_diff_status(comparison_id):
    task = AsyncResult(read_meta(comparison_id)['task_id'])
    return jsonify(
        {
            'status': 'pending' if not task.ready() else ('error' if task.failed() else 'done'),
            'error': str(task.result) if task.failed() else None,
        }
    )


@document_diff.route('/file/<string:comparison_id>/<path:filename>')
@_protected
def document_diff_file(comparison_id, filename):
    meta = read_meta(comparison_id)
    allowed = (
        {f'{comparison_id}_1_hl.pdf', f'{comparison_id}_2_hl.pdf', f'{comparison_id}_diff.docx'}
        if meta['fmt'] == 'docx'
        else {f'{comparison_id}_diff_highlighted.pdf'}
    )
    for item in meta.get('mapping', []):
        allowed.update(
            f'{comparison_id}_{side}_slide_{item[field]}.png'
            for field, side in (('slide_a', 'a'), ('slide_b', 'b'))
            if item.get(field) is not None
        )
    if filename not in allowed:
        abort(404)
    return send_from_directory(
        UPLOAD_FOLDER, filename, as_attachment=request.args.get('download') == '1', download_name=filename
    )


@document_diff.route('/<string:first_id>/<string:second_id>')
@_protected
def document_diff_page(first_id, second_id):
    if first_id == second_id:
        return 'Для сравнения выберите два разных документа', 400
    try:
        comparison_id = create_comparison('docx', {'first_document_id': first_id, 'second_document_id': second_id}, {})
    except ValueError:
        return render_template('404.html'), 404
    return redirect(url_for('document_diff.document_diff_result', comparison_id=comparison_id))
