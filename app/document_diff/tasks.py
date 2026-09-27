from os.path import join

from bson import ObjectId

from app.db.methods import check as check_methods
from app.db.methods import file as file_methods
from app.document_diff.docx_diff import compare_docx
from app.document_diff.pptx_diff import compare_pptx
from app.utils.converter import convert_to
from app.tasks import FILES_FOLDER, celery, logger, remove_files


@celery.task(name='compare_documents', queue='document-diff', bind=True, max_retries=1)
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
                path = convert_to(path, target_format=format_name)
                if path is None:
                    raise ValueError('Не удалось преобразовать документ для сравнения')
                temporary_paths.append(path)
            if format_name == 'docx':
                pdf_id = check.conv_pdf_fs_id if check_id else source['pdf_id']
                file_methods.write_file_from_db_file(ObjectId(pdf_id), join(FILES_FOLDER, f'{comparison_id}_{number}_hl.pdf'))
            documents.append(path)
        compare = compare_docx if format_name == 'docx' else compare_pptx
        return compare(*documents, comparison_id)
    except Exception as error:
        logger.error('document_diff: ошибка сравнения comparison_id=%s: %s', comparison_id, error, exc_info=True)
        raise
    finally:
        remove_files(temporary_paths)
