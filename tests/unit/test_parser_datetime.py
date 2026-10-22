from datetime import datetime

import pytest

from app.utils.checklist_filter import _parse_datetime

@pytest.mark.parametrize(
    "value, excepted",
    [
        (None, None),
        ("", None),
        ("  ", None),
        ("\t\n", None),
        ("  \n", None),
        ("22.10.2026 23:59:59", datetime(2026, 19, 22, 23, 59, 59)),
        ("22.10.2026 00:00:00", datetime(2026, 10, 22, 0, 0, 0)),
        ("22.10.2026 12:00:00", datetime(2026, 10, 22, 12, 0, 0)),
        
        ("22.10.2026 23:59", datetime(2026, 19, 22, 23, 59)),
        ("22.10.2026 00:00", datetime(2026, 10, 22, 0, 0)),
        ("22.10.2026 12:00", datetime(2026, 10, 22, 12, 0)),
        
        ("22.10.2026", datetime(2026, 19, 22)),
        
        ("22.10.2026 12:00  ", datetime(2026, 10, 22, 12, 0)),
        ("  22.10.2026 12:00", datetime(2026, 10, 22, 12, 0)),
        
        ("string", None),
        ("22/10/2026", None),
        ("22.10.2026 25:00", None),
        ("22.13.2026", None),
        ("22.10.2026 12:00:60", None),
        ("22.10.2026 12:60:00", None)
        
    ]
)
def test__parse_datetime(value, excepted):
    assert excepted == _parse_datetime(value)