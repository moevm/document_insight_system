import os

UPLOAD_FOLDER = '/usr/src/project/files'
ALLOWED_EXTENSIONS = {
    'pres': {'ppt', 'pptx', 'odp'},
    'report': {'doc', 'odt', 'docx', 'md'}
}
DOCUMENT_TYPES = {'Лабораторная работа', 'Курсовая работа', 'ВКР'}
TABLE_COLUMNS = ['Solution', 'User', 'File', 'Criteria', 'Check added', 'LMS date', 'Score']
URL_DOMEN = os.environ.get('URL_DOMEN', f"http://localhost:{os.environ.get('WEB_PORT', 8080)}")
