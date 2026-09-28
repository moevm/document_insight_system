import os
from os.path import join

from bson import ObjectId
from celery import shared_task

from app.db.methods import check as check_methods
from app.db.methods import file as file_methods
from app.document_diff.docx_diff import compare_docx
from app.document_diff.pptx_diff import compare_pptx
from app.tasks import FILES_FOLDER, libreoffice_lock, logger, remove_files
from app.utils.converter import convert_to


def _result_filenames(comparison_id, format_name, result):
    if format_name == 'docx':
        return [
            f'{comparison_id}_1_hl.pdf',
            f'{comparison_id}_2_hl.pdf',
            f'{comparison_id}_diff.docx',
        ]
    filenames = {f'{comparison_id}_diff_highlighted.pdf'}
    for item in result['mapping']:
        for side, field in (('a', 'slide_a'), ('b', 'slide_b')):
            if item[field] is not None:
                filenames.add(f'{comparison_id}_{side}_slide_{item[field]}.png')
    return sorted(filenames)


def _store_result_files(comparison_id, format_name, result):
    stored_files = {}
    for filename in _result_filenames(comparison_id, format_name, result):
        path = join(FILES_FOLDER, filename)
        if not os.path.exists(path):
            raise ValueError(f'Не найден файл результата сравнения: {filename}')
        stored_files[filename] = str(file_methods.add_file_to_db(filename, path))
    return stored_files


@shared_task(name='compare_documents', queue='document-diff', bind=True, max_retries=1)
def compare_documents(self, comparison_id, format_name, first_source, second_source):
    if format_name not in ('docx', 'pptx'):
        raise ValueError('Неизвестный формат сравнения')
    temporary_paths, documents = [], []
    try:
        for number, source in enumerate((first_source, second_source), 1):
            path = join(FILES_FOLDER, f'{comparison_id}_{number}.{source["extension"]}')
            temporary_paths.append(path)
            check_id = source.get('check_id')
            if check_id:
                check = check_methods.get_check(ObjectId(check_id))
                if check is None:
                    raise ValueError('Документ не найден в системе')
                file_methods.write_file_from_db_file(check._id, path)
            if source['extension'] != format_name:
                with libreoffice_lock():
                    path = convert_to(path, target_format=format_name)
                if path is None:
                    raise ValueError('Не удалось преобразовать документ для сравнения')
                temporary_paths.append(path)
            if format_name == 'docx':
                highlight_path = join(FILES_FOLDER, f'{comparison_id}_{number}_hl.pdf')
                if check_id:
                    file_methods.write_file_from_db_file(ObjectId(check.conv_pdf_fs_id), highlight_path)
                else:
                    with libreoffice_lock():
                        pdf_path = convert_to(path, target_format='pdf')
                    if pdf_path is None:
                        raise ValueError('Не удалось преобразовать документ в PDF')
                    temporary_paths.append(pdf_path)
                    if pdf_path != highlight_path:
                        os.replace(pdf_path, highlight_path)
                temporary_paths.append(highlight_path)
            elif check_id:
                pdf_path = join(FILES_FOLDER, f'{comparison_id}_{number}.pdf')
                file_methods.write_file_from_db_file(ObjectId(check.conv_pdf_fs_id), pdf_path)
                temporary_paths.append(pdf_path)
            else:
                with libreoffice_lock():
                    pdf_path = convert_to(path, target_format='pdf')
                if pdf_path is None:
                    raise ValueError('Не удалось преобразовать презентацию в PDF')
                temporary_paths.append(pdf_path)
            documents.append(path)
        compare = compare_docx if format_name == 'docx' else compare_pptx
        result = compare(*documents, comparison_id)
        result_files = _result_filenames(comparison_id, format_name, result)
        temporary_paths.extend(join(FILES_FOLDER, filename) for filename in result_files)
        result['files'] = _store_result_files(comparison_id, format_name, result)
        return result
    except Exception as error:
        logger.error('document_diff: ошибка сравнения comparison_id=%s: %s', comparison_id, error, exc_info=True)
        raise
    finally:
        remove_files(temporary_paths)
