# Разбор отчётов

Основной вход — `app/main/parser.py`: DOC и ODT конвертируются в DOCX через
LibreOffice; DOCX и Markdown разбираются своими загрузчиками.

- `docx_uploader` читает текст, таблицы и оформление Word.
- `md_uploader` читает Markdown и получает число страниц из PDF после конвертации.
- `pdf_document` извлекает текст и изображения по страницам PDF.
- `document` строит дерево разделов и объектов документа.

PDF нужен как вспомогательный файл; самостоятельная загрузка PDF как отчёта
не поддерживается. Markdown не содержит геометрии и стилей Word.

Зависимости, запуск и API описаны в [README](../../../README.md).
Проверки разборщиков запускаются из корня проекта:

```bash
PYTHONPATH=app:. .venv/bin/pytest -p no:cacheprovider -c /dev/null --rootdir=. --import-mode=importlib -q tests/criteria tests/reports
```

Тесты подменяют внешнюю конвертацию. Реальный путь загрузки, LibreOffice и GridFS
проверяет `scripts/verify_deployment.py`; условия запуска — в основном README.
