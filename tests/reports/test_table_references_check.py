from types import SimpleNamespace

import pytest

from app.main.checks.report_checks.table_references import TableReferences


@pytest.mark.parametrize('reference, score', [('См. таблицу 1.', 1), ('Нет ссылки.', 0), ('См. таблицу 2.', 0)])
def test_table_references(reference, score):
    children = [
        {'style': 'вкр_подпись таблицы', 'text': 'Таблица 1 — Данные'},
        {'style': 'body text', 'text': reference},
    ]
    file = SimpleNamespace(make_chapters=lambda _: [{'text': 'Раздел', 'child': children}], file=None)
    info = {'file': file, 'file_type': {'type': 'report', 'report_type': 'VKR'}}
    assert TableReferences(info).check()['score'] == score
