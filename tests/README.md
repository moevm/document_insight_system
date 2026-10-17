# Проверка Document Insight System

Команды выполняются из корня проекта. Python — 3.12, frontend — Node.js 20.
Общая настройка окружения описана в [README](../README.md#разработка-и-проверки).

## Критерии и разборщики

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
PYTHONPATH=app:. .venv/bin/pytest -p no:cacheprovider -c /dev/null --rootdir=. --import-mode=importlib -q tests/criteria tests/reports
python3 scripts/test_versioning.py
make check-version
```

`tests/criteria` содержит регрессионные сценарии с генерируемыми документами.
`tests/reports` использует также синтетические файлы из `tests/fixtures/reports`;
они должны входить в Git вместе с тестами. Конвертация MD, LanguageTool и HTTP-запросы
подменяются на границах внешних сервисов. Наличие положительных тестов не подтверждает
работу реальных LibreOffice, LanguageTool или LTI passback.

Не запускайте весь `tests` обычным pytest: в корне находятся Selenium-сценарии,
импорт которых создаёт браузер, а в `tests/reports` есть отдельный `pytest.ini`.
Для этих групп используются разные команды запуска.

## Selenium

Сценарии работают с запущенным web и действующей БД: создают проверки и могут менять
наборы критериев. Используйте отдельное тестовое развёртывание и его учётные данные.

В Docker:

```bash
cp .env_example .env  # только для нового тестового окружения, не поверх рабочего .env
# Настройте отдельные порты, COMPOSE_PROJECT_NAME и путь данных MongoDB.
make tests
bash tests/scripts/docker_check_tests.sh
```

Важно: один `COMPOSE_PROJECT_NAME` изолирует named volume, но стандартный bind mount
MongoDB всё ещё указывает на `../dis_mongo_data`. Для отдельной БД переопределите этот
mount в тестовом Compose-файле или используйте отдельную копию проекта в другом каталоге.
`make tests` собирает образы и запускает контейнеры в фоне. Скрипт ожидания проверяет
код завершения `selenium-tests`; запуск контейнера сам по себе не означает успех тестов.

Для локального браузера нужны Chrome/Chromium и отдельные зависимости Selenium:

```bash
.venv/bin/python -m pip install -r tests/requirements.txt
.venv/bin/python tests/main.py --host http://localhost:8080 --login admin --password TEST_PASSWORD
```

`TEST_PASSWORD` — placeholder. `webdriver-manager` может обращаться к сети за драйвером.
Можно передать свои файлы через `--pres`, `--report` и `--report_doc`; по умолчанию берутся
`tests/tests_data/example_of_pres.pptx`, `example_of_report.docx`, `example_of_report.doc`.
Загрузка проверяется для типа набора текущего пользователя; несовпадающий тип пропускается.

Покрываются вход, список и карточка проверки, загрузка, страницы наборов/критериев
и `/version/`. Тест версии ищет таблицу `version-table`; JSON-файл версии не используется.
Список запускаемых классов находится в [main.py](main.py).

## Сквозной HTTP/API-сценарий
Команда и побочные эффекты описаны в [README](../README.md#сквозной-сценарий):

```bash
docker compose exec -T web python3 - < scripts/verify_deployment.py
```

Сценарий создаёт три проверки в текущей БД и проверяет реальные конвертацию,
Celery, GridFS, результаты, PDF, журналы и совместимость загрузки с `access_token`.
Он не заменяет Selenium и не проверяет возврат оценки в LMS.
