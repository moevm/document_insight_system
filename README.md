# Document Insight System

DIS проверяет учебные отчёты и презентации по настраиваемым наборам критериев: структуру,
оформление, ссылки, объём и отдельные свойства текста. Проверка выполняется в фоне;
результат содержит оценку, замечания и ссылки на страницы PDF. Есть web-интерфейс,
интеграция LTI и загрузка Markdown через API с `access_token`.

- [Критерии и настройка наборов](docs/criteria.md) — 39 проверок отчётов и 23 проверки презентаций.
- [Изменения и миграция к 3.0.0](CHANGELOG.md).
- [План ближайших версий](docs/ROADMAP.md).
- [Правила работы с репозиторием](AGENTS.md).

## Что можно загрузить

| Тип набора | Исходный файл | Обработка |
|---|---|---|
| `report`, `VKR` или `LR` | DOCX, DOC, ODT | DOC/ODT преобразуются в DOCX. Структура и оформление читаются из DOCX, страницы — из PDF. |
| `report`, обычно `VKR` для SW | MD | Разбор Markdown и генерация PDF через md2pdf. Нужен набор критериев для этого задания. |
| `pres` | PPTX, PPT, ODP | PPT/ODP преобразуются в PPTX, проверяются слайды. |

PDF служит для просмотра и проверок страниц; самостоятельная загрузка PDF вместо исходника
не поддерживается. Web-загрузка может принимать дополнительный PDF вместе с исходником.
Лимит HTTP-запроса по умолчанию — 16 МБ, лимит хранилища — 50 000 МБ
([app/config.ini](app/config.ini)). Текст внутри изображений не распознаётся.

Проверки содержания используют словари, морфологию и лексическое сходство. Они помогают
найти формальные проблемы, но не заменяют содержательную оценку работы преподавателем.

## Первый запуск

Понадобятся Docker Engine, Compose v2, GNU Make, Python 3 и Git на хосте.
Compose рассчитан на Linux: в контейнеры монтируются `/etc/timezone` и `/etc/localtime`.
Системные библиотеки обработки документов устанавливаются при сборке образов.

```bash
cp .env_example .env
# Отредактируйте .env перед запуском.
make build-all
make full-up-d
```

Откройте `http://localhost:8080` и войдите как `admin` с паролем из `ADMIN_PASSWORD`.
Адрес изменится, если задан другой `WEB_PORT`. При первом запуске web применяет миграции
MongoDB и создаёт администратора. Изменение `ADMIN_PASSWORD` в `.env` не меняет пароль
уже существующей учётной записи в БД.

`make full-up-d` добавляет LanguageTool к основным сервисам. Для запуска без него используйте
`make up-d`: орфографическая проверка будет выдавать предупреждение о недоступности сервиса.
Оба варианта запускают контейнеры в фоне.

### Настройки `.env`

Значения секретов в `.env_example` — примеры; замените их для своего развёртывания.
Не добавляйте `.env` в Git.

| Переменная | Назначение |
|---|---|
| `COMPOSE_PROJECT_NAME` | Пространство имён Compose, включая имена volume. Сохраняйте при обновлении. |
| `SECRET_KEY`, `ADMIN_PASSWORD` | Секрет сессий и начальный пароль администратора. |
| `SIGNUP_PAGE_ENABLED` | Доступность страницы регистрации. |
| `WEB_PORT` | Внешний порт web, по умолчанию `8080`. |
| `REDIS_URL` | Broker и backend Celery, обычно `redis://redis:6379/0`. |
| `CELERY_QUERIES` | Список обслуживаемых очередей через запятую; обычная обработка требует `check-solution,convert-pdf`. |
| `ACCESS_TOKEN` | Общий токен внешних систем для загрузки и экспорта. |
| `CONSUMER_KEY`, `CONSUMER_SECRET` | Учётные данные интеграции LTI. |
| `FLOWER_PORT`, `FLOWER_PREFIX`, `FLOWER_AUTH`, `FLOWER_SECRET_KEY` | Внешний порт, префикс, basic auth и секрет панели Flower. Внутренний порт — `5555`. |
| `CONTAINER_CPU`, `WORKER_MEMORY`, `MONGODB_CACHE_SIZE` | CPU affinity, лимит памяти worker и размер кэша MongoDB в ГБ. |
| `IMAGE_VERSION` | Производное служебное поле. Make записывает его из `package.json`; вручную менять не нужно. |

Для корня Flower допустимы пустой `FLOWER_PREFIX` и `/`; значения `flower`, `/flower`
и `/flower/` задают адрес `/flower/`. Внешние слеши нормализуются при запуске.

Для LTI passback дополнительно требуется потребитель очереди `passback-grade`: стандартный
список очередей в примере её не включает. Возврат оценки в LMS проверяйте отдельно от загрузки.

Орфография обращается к `http://languagetool:8010`. Для другого адреса передайте
`LANGUAGETOOL_URL` **в окружение worker** через Compose. Простая запись в `.env` этого
не делает: worker не подключает весь файл через `env_file`.

### Сервисы и данные

Путь обработки: web сохраняет загрузку → Redis/Celery передают задачу worker → worker
конвертирует документ, запускает критерии и сохраняет результат в MongoDB/GridFS → web
показывает результат и PDF. Flower отображает состояние Celery.

| Данные | Место хранения |
|---|---|
| Общие рабочие файлы web/worker | Named volume `files`, `/usr/src/project/files` внутри контейнеров. |
| Результаты, исходники и PDF в GridFS | MongoDB, bind mount `../dis_mongo_data`. |
| Данные Redis | Named volume `redis_data`. |
| История Flower | Named volume `flower_data`, `/etc/db`. |

Резервная копия должна учитывать MongoDB/GridFS и файловые volume. Один каталог `files`
не содержит всей истории проверок. Не меняйте имя Compose-проекта или путь MongoDB
при обновлении без переноса соответствующих данных.

```bash
docker compose ps
docker compose logs --tail=100 web worker
docker compose logs -f worker
make down
```

`volumes-init` со статусом `Exited (0)` — штатное завершение подготовки прав.
Web и worker ждут успешных healthcheck Redis/MongoDB и завершения init-сервиса.
При ошибке миграции БД web завершает запуск; причина будет в его журнале.

## Обновление существующего развёртывания

Сначала сохраните резервную копию данных и `.env`, затем соберите образы:

```bash
make build-all
```

Web, worker и Flower работают как `app` с UID/GID `10001:10001`. При первом переходе
со старых образов остановите процессы, которые ещё могут создавать файлы от root,
и подготовьте существующие volume:

```bash
docker compose stop web worker worker-dashboard
docker compose run --rm --no-deps volumes-init
make full-up-d  # либо make up-d без LanguageTool
```

Init-сервис меняет владельцев `files` и `flower_data`, добавляет владельцу чтение/запись,
каталогам — право прохода. Содержимое файлов сохраняется, симлинки не разыменовываются.
Он работает от root без сети и монтирует только эти два volume. При обычном запуске
подготовка выполняется автоматически; повторное выполнение допустимо.

Не используйте `down -v` для миграции прав: команда удаляет named volume.
`docker compose restart` не применяет новый образ или `USER`; после сборки нужен `up`.
При прямом `docker run` подготовку прав нужно выполнить отдельно.

Проверка пользователя и доступа:

```bash
docker compose exec -T web sh -c 'id; test -r files && test -w files && test -x files'
docker compose exec -T worker sh -c 'id; test -r files && test -w files && test -x files'
```

Ожидаемый UID/GID — `10001:10001`. Для проверки реальной загрузки и чтения результата
используйте сквозной сценарий ниже. Совместимость существующих наборов описана
в [миграции критериев](CHANGELOG.md#миграция-существующих-наборов).

## API для внешних систем

### Загрузка с `access_token`

`POST /tasks/md` принимает `multipart/form-data`, не требует cookie-сессии и использует
тип `report/VKR`. Передайте:

| Поле формы | Значение |
|---|---|
| `file` | Исходный Markdown-файл. |
| `access_token` | Значение `ACCESS_TOKEN` сервера. Именно поле формы, а не Bearer-заголовок. |
| `criteria` | Имя существующего набора критериев. |
| `full_response` | Необязательное непустое значение для JSON-ответа. |

```bash
# DIS_ACCESS_TOKEN задаётся отдельно.
DIS_URL=http://localhost:8080
DIS_CRITERIA=BaseReportCriterionPack
curl --fail-with-body "$DIS_URL/tasks/md" \
  --form 'file=@work.md' \
  --form-string "access_token=$DIS_ACCESS_TOKEN" \
  --form-string "criteria=$DIS_CRITERIA"
```

Ответ по умолчанию — **строка `check_id`**, без JSON-обёртки. Этот режим сохранён для
существующих клиентов. Для Markdown обычно нужен свой набор: базовый отчётный набор
содержит требования к ВКР в DOCX и может выставить MD нулевой балл.

Добавление `--form-string 'full_response=1'` возвращает:

```json
{"task_id": "celery-task-id", "check_id": "0123456789abcdef01234567"}
```

Любая непустая строка включает JSON-режим, в том числе `full_response=false`.
Для строкового ответа опустите поле. Неверный или отсутствующий токен даёт HTTP 401.
Некоторые ошибки валидации возвращаются строками с HTTP 200, например
`not_allowed_extension`, `mime_type_does_not_match_extension`, `storage_overload`.
Проверяйте содержимое ответа перед использованием его как `check_id`.

### Готовность и получение результата

| Маршрут | Доступ и ответ |
|---|---|
| `GET /api/results/ready/<check_id>` | Без сессии; JSON `{"is_ended": false}` или `true`. Завершение не гарантирует успешную проверку или проходной балл. |
| `GET /results/svg/<check_id>` | Без сессии; SVG со статусом или итоговой оценкой. |
| `GET /results/<check_id>` | HTML-результат, нужна авторизация. Результаты API доступны авторизованным пользователям. |
| `GET /tasks/<task_id>` | Статус Celery, нужна авторизация. `task_id` отличается от `check_id`. |
| `GET /api/results/logs/<check_id>` | Журнал JSON, нужна авторизация и доступ к проверке; параметры `limit` (1–200), `offset`, `levels`. |
| `GET /get_pdf/<conv_pdf_fs_id>` | PDF, нужна авторизация. Идентификатор PDF отличается от `check_id`. |
| `GET /get_csv/?access_token=…` | Статистика CSV; токен в query или сессия администратора. |
| `GET /get_zip/?access_token=…` | ZIP с исходными файлами и статистикой; тот же доступ. Это не архив всех конвертированных PDF. |

Внешний клиент может опрашивать готовность и получать SVG по `check_id`. Токен загрузки
не заменяет авторизацию на HTML/PDF/журналах. Публичного JSON-маршрута со всеми результатами
критериев в текущем API нет. Query-токен экспорта может попадать в журналы HTTP.

Для web-клиентов `POST /tasks/` требует cookie-сессию, принимает `file`, необязательный
`pdf_file` и возвращает `task_id`/`check_id`. Тип и набор определяются настройками пользователя.
Вход `POST /login/` принимает JSON `username` и `password_hash` — MD5 пароля, как в
существующем клиенте; это не формат токена загрузки.

## Настройка критериев

Набор задаёт тип документа, порог `min_score` и `raw_criterions`. Администратор управляет
наборами через интерфейс. Пример структуры небольшого набора:

```json
{
  "name": "MarkdownExample",
  "file_type": {"type": "report", "report_type": "VKR"},
  "min_score": 1.0,
  "raw_criterions": [
    ["simple_check"],
    ["report_was_were_check", {"threshold": 3}],
    ["spelling_check"]
  ]
}
```

Это пример конфигурации, а не тело запроса создания набора. В `POST /api/criterion_pack`
используются поля формы `pack_name`, `file_type`, `report_type`, `min_score` и JSON-строка
`raw_criterions`; маршрут доступен администратору.

Итог — среднее обычных критериев; ноль обязательного критерия обнуляет весь набор.
Рекомендательные проверки исключаются из среднего. Неизвестные ID и неверные параметры
дают видимую ошибку настройки. Состав, параметры, карты заголовков и примеры SW —
в [справочнике критериев](docs/criteria.md).

## Разработка и проверки

Python-код рассчитан на Python 3.12, frontend — на Node.js 20.

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes -r requirements.lock
.venv/bin/python -m pip install ruff
PYTHONPATH=app:. .venv/bin/pytest -p no:cacheprovider -c /dev/null --rootdir=. --import-mode=importlib -q tests/criteria tests/reports
.venv/bin/ruff check app/main/checks app/main/check_packs app/main/reports app/main/presentations app/nlp tests/criteria tests/reports tests/util
python3 scripts/test_versioning.py
npm ci
npm run build
```

Тесты критериев используют документы DOCX/PPTX/PDF, но подменяют конвертацию MD,
LanguageTool и сетевые запросы на границах внешних сервисов. Они не заменяют проверку
всего развёртывания. Правила Ruff находятся в [ruff.toml](ruff.toml).
Для импортов нужны оба пути `PYTHONPATH=app:.`: в проекте есть `app.*` и старые импорты.

[docker-compose-dev.yml](docker-compose-dev.yml) монтирует код `app` и открывает MongoDB
для разработки. Он не добавляет автоматическую пересборку frontend. Selenium использует
отдельные [зависимости](tests/requirements.txt) и [Compose-файл](docker-compose-selenium.yml).
`make tests` собирает и запускает это окружение в фоне; сам факт запуска не означает
успешное завершение UI-тестов. Команды и границы UI-проверок описаны в [tests/README.md](tests/README.md).

### Сквозной сценарий

После запуска реальных сервисов:

```bash
docker compose exec -T web python3 - < scripts/verify_deployment.py
```

Сценарий использует текущие `ADMIN_PASSWORD` и `ACCESS_TOKEN` контейнера без вывода секретов.
Он создаёт **три проверки в действующей БД**, оставляет их результаты для просмотра и проверяет:
DOCX через web, Markdown через оба режима API, обработку Celery, отсутствие внутренних
ошибок критериев, GridFS, PDF, HTML/SVG, журналы, CSV/ZIP и отказ с неверным токеном.
Отчёт сохраняется в `/tmp/dis-e2e-report.json` внутри web-контейнера.
Нулевой балл документа допустим; ошибка пайплайна приводит к ненулевому коду завершения.
LTI passback и полный набор UI-сценариев этим скриптом не проверяются.

### Обновление зависимостей

`package-lock.json` фиксирует дерево npm; Docker устанавливает его через `npm ci`.
При изменении зависимостей в `package.json` обновите lock на Node.js 20:

```bash
npm install --package-lock-only --ignore-scripts --include=dev --no-audit --no-fund
npm ci
npm run build
```

`requirements.txt` — входной список Python-зависимостей, `requirements.lock` — точные
транзитивные версии с SHA-256 для Linux/Python 3.12. Для обновления lock:

```bash
python3.12 -m venv .venv-lock
.venv-lock/bin/python -m pip install pip==25.3 pip-tools==7.6.2
.venv-lock/bin/pip-compile --generate-hashes --allow-unsafe --strip-extras --no-emit-index-url --no-emit-trusted-host --output-file=requirements.lock requirements.txt
```

Без дополнительных флагов подходящие существующие версии сохраняются. Для обновления
всего дерева добавьте `--upgrade`, одной зависимости — `--upgrade-package имя`.
После обновления проверьте тесты и сборку web/worker. Оба lock-файла хранятся в Git.
Они не фиксируют apt-пакеты, базовые образы и инструменты изолированной сборки Python.

## Версия приложения и сборка

Меняйте **только `version` в [package.json](package.json)**, в формате `MAJOR.MINOR.PATCH`.
При несовместимых изменениях повышайте MAJOR, новых совместимых возможностях — MINOR,
совместимых исправлениях — PATCH. Текущая подготовленная версия — 3.0.0.

```bash
# После изменения package.json:
make sync-version
make check-version
make build-all
make full-up-d
```

Сборка и запуск через Make сами выполняют синхронизацию: обновляют два поля версии
в `package-lock.json` и `IMAGE_VERSION` в существующем локальном `.env`, сохраняя зависимости,
хеши и остальные настройки. Если `.env` отсутствует, синхронизация его не создаёт.
В Git сохраняйте манифест вместе с lock-файлом.

| Команда | Действие |
|---|---|
| `make build-all` | Сначала собирает worker-base, затем web и worker. Используйте после изменения базы. |
| `make build` | Собирает web и worker. При отсутствии worker-base пытается скачать его, затем собрать локально. |
| `make build-web`, `make build-worker`, `make build-base` | Сборка отдельных образов. |
| `make up-d`, `make full-up-d` | Запуск без/с LanguageTool в фоне; без сборки образов. |
| `make check-version` | Проверка согласованности без записи файлов. |

Из версии манифеста получаются теги `dis:web-image-<версия>`, `dis:worker-image-<версия>`
и `dvivanov/dis:worker-base-<версия>`. Make передаёт build args для версии, commit, даты,
ветки и состояния исходников; Docker labels и `/version/` используют эти метаданные.
Незакоммиченные изменения отражаются как `dirty`.

Перед ручным `docker compose build/up` после смены версии выполните `make sync-version`.
Compose читает `.env`, а не JSON. Прямой `docker build` требует `IMAGE_VERSION` как build arg;
значение можно получить через `python3 scripts/check_versions.py --print-version`.
Без остальных build args сведения об исходниках будут `unknown`. Make всегда берёт версию
из манифеста, игнорируя старое переопределение `IMAGE_VERSION` из окружения или командной строки.

`/version/` читает `APP_VERSION`, `APP_COMMIT`, `APP_BUILD_DATE`, `APP_BRANCH`, `APP_SOURCE_STATE`
из образа. При запуске вне Docker версия берётся из `package.json`, остальные неизвестные
поля показываются как `unknown`. Дополнительные JSON-файлы версии не нужны.

CI проверяет согласованность и для релизного тега — совпадение `v<версия>` с манифестом.
Схема MongoDB и версии библиотек независимы от версии DIS. Git-теги, PR, GitHub Release
и публикация образов выполняются отдельно: локальная сборка их не создаёт.

## Где искать код

| Путь | Назначение |
|---|---|
| [app/main/checks](app/main/checks) | Реестр и реализации критериев. |
| [app/main/check_packs](app/main/check_packs) | Создание критериев, базовые наборы и подсчёт оценки. |
| [app/main/reports](app/main/reports), [app/main/presentations](app/main/presentations) | Модели и разбор документов. |
| [app/nlp](app/nlp) | Морфология и сравнение текста. |
| [app/tasks.py](app/tasks.py) | Конвертация и проверка в Celery. |
| [app/routes](app/routes), [app/templates](app/templates) | HTTP-маршруты и интерфейс. |
| [db_versioning](db_versioning) | Миграции MongoDB. |
| [scripts](scripts) | Запуск, права volume, версии и проверка развёртывания. |
| [tests/criteria](tests/criteria), [tests/reports](tests/reports) | Тесты критериев и разборщиков. |
