# Тесты критериев отчётов

Актуальные команды запуска, фикстуры и ограничения тестирования описаны
в [tests/README.md](README.md).

Поведение критериев и их параметры — в [справочнике](../docs/criteria.md),
изменения совместимости — в [CHANGELOG](../CHANGELOG.md).

В CI критерии и разборщики запускаются заданием `criteria` из
[build.yml](../.github/workflows/build.yml). Оно использует `requirements.lock`
и проверяет `tests/criteria` вместе с `tests/reports`.
