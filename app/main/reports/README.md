# Запуск и тестирование

Пререквизиты: `argparse`, `python-docx`, `docx2python`, `re`, `subprocess`, `markdown`. Для парсинга `.doc`-файлов потребуется
LibreOffice.

Здесь и далее считается, что корневая директория репозитория добавлена в `PYTHONPATH`.

Код проверки текстовых документов разбит по python-пакетам:

## `docx_uploader`

Proof-of-concept парсинг файлов `.docx` с выводом структуры
файла в текстовом виде в stdout.

Запуск: `python3 -m app.main.mse22.docx_uploader [--help|-h] docx_parser --file <path_to_docx_file>`

Конкретные примеры:

`python3 -m app.main.mse22.docx_uploader docx_parser --file ~/my/beatiful/file.docx`
– парсинг файла `~/my/beatiful/file.docx`;

`python3 -m app.main.mse22.docx_uploader --help`
– вызов краткой справки;

`python3 -m app.main.mse22.docx_uploader docx_parser --file ~/my/beatiful/file.docx > /dev/null && echo $?`
– проверка безошибочной работы пакета на файле `~/my/beatiful/file.docx` без
вывода содержимого файла.

## `doc`

Перевод файлов `.doc`, `.odt` в `.docx` с помощью сторонней программы (LibreOffice) с целью дальнейшего парсинга.

`python3 -m app.main.mse22.converter_to_docx convert --filename <path_to_file>`

Пример: `python3 -m app.main.mse22.converter_to_docx convert --filename ~/my/beatiful/file.doc`

## `document`

Парсинг файлов с созданием вспомогательных структур, которые будут
использоваться для проверки документов, с печатью результата в stdout.

Запуск: `python3 -m app.main.mse22.document [-h|--help] --filename <path_to_docx_file> --type <type_of_file>`

Тип файла:

- LR - Лабораторная работа
- FWQ - Выпускная квалификационная работа

Конкретные примеры:

`python3 -m app.main.mse22.document --help`
– вызов краткой справки;

`python3 -m app.main.mse22.document --filename ~/my/beatiful/file.docx --type FWQ`
– парсинг файла `~/my/beatiful/file.docx`;

`python3 -m app.main.mse22.document --filename ~/my/beatiful/file.docx --type FWQ > /dev/null && echo $?`
– проверка безошибочной работы пакета на файле `~/my/beatiful/file.docx` без
вывода содержимого файла.

## `PDF`

Получаем текст по страницам из файла с помощью конвертации файла в pdf.

```bash
$ python3 -m app.main.mse22.pdf_document text_from_pages --filename path_to_file
```

## `MD`

Парсинг файлов `.md` с выводом структуры файла в текстовом виде в stdout.

```bash
$ python3 -m app.main.reports.md_uploader md_parser --mdfile path_to_md_file
```

