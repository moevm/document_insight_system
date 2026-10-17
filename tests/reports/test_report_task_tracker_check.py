from types import SimpleNamespace

from app.main.checks.report_checks.task_tracker import ReportTaskTracker


def criterion(tasks=None, title='Введение'):
    children = [
        {'text': 'Задачи исследования:'},
        *[{'text': text} for text in (tasks or [])],
        {'text': 'Объект исследования: система'},
    ]
    file = SimpleNamespace(page_counter=lambda: 4, make_chapters=lambda _: [{'text': title, 'child': children}])
    return ReportTaskTracker({'file': file, 'file_type': {'type': 'report', 'report_type': 'VKR'}})


def test_valid_report():
    assert criterion(['Исследовать систему', 'Сравнить аналоги']).check()['score'] == 1


def test_forbidden_words():
    assert criterion(['Решить, проблему']).check()['score'] == 0


def test_missing_chapter():
    assert criterion(['Исследовать систему'], title='Другой раздел').check()['score'] == 0
