# Проверка разрешения конфликта PR #878 — 2026-10-24

Завершено начатое слияние `dev` в `797_fix_decimal_places_check`.
Первый родитель merge-коммита — `eab2412b986d7edca5d9b30d7745fc311c3d05c6`,
второй — `415836babcf08db77bcadac930ee26fb74f55f4a` (слияние pre-release в dev).
Эта запись относится к merge-коммиту, впервые добавившему данный файл.

## Изменения

- Сохранены регулярное выражение, проверка разделителей и подсчёт дробных знаков
  из pre-release: знак числа, длинная целая часть и смешанные разделители.
- Из PR сохранены исключения URL http/https, DOI (`DOI:`, `doi.org/`) и номеров ГОСТ.
- Добавлены регрессионные проверки для отчётов и презентаций: исключения не скрывают
  обычные числа после идентификатора; повторный вызов даёт тот же результат.
- Сохранён сценарий числа с единицей без пробела, но ожидание согласовано с алгоритмом
  pre-release: `1.2345мм` не является самостоятельным числом. Дополнительно проверяется
  нарушение в `1.2345 мм` и смешанный разделитель после нескольких исключений.
- Обновлены [справочник критериев](criteria.md) и [CHANGELOG](../CHANGELOG.md).

До разрешения конфликта все staged-файлы вне конфликтного модуля сопоставлены
с автоматическим результатом `git merge-tree`: посторонних staged-изменений не найдено.
Локальные скрипты, Jenkinsfile и материалы reviews в merge-коммит не добавляются.

## Команды и результат

```bash
PYTHONPATH=app:. .venv/bin/pytest -p no:cacheprovider -c /dev/null --rootdir=. --import-mode=importlib -q tests/criteria tests/reports
.venv/bin/ruff check app/main/checks app/main/check_packs app/main/reports app/main/presentations app/nlp tests/criteria tests/reports tests/util
.venv/bin/ruff check app/utils/decimal_places_check.py
.venv/bin/ruff format --check app/utils/decimal_places_check.py tests/criteria/test_pipeline_regressions.py tests/reports/test_decimal_places_check.py
.venv/bin/ruff check .
.venv/bin/ruff format --check .
git diff --check
```

- Pytest: **195 passed**; предупреждения DeprecationWarning зависимостей.
- Выборочные Ruff check и format: успешно.
- Полный Ruff format: успешно, 236 файлов.
- Полный Ruff check: одна E501 в локальном `run_recheck.py:1575`, вне задачи;
  этот незакоммиченный скрипт не изменялся.
- Пробельные ошибки и относительные ссылки изменённой документации проверены.

## Ограничения

Тесты используют подмены внешних сервисов. Реальная конвертация и API в Docker,
пользовательская БД, миграции, LTI passback и развёртывание не проверялись.
Frontend и зависимости не менялись. Версия приложения не менялась.
Коммит создаётся локально, push не выполняется.
