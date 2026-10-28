from datetime import datetime, timedelta

import pytest

from app.utils.checklist_filter import _parse_bounds, _parse_datetime, _start_of_next_day


@pytest.mark.parametrize(
    "value, excepted",
    [
        (None, None),
        ("", None),
        ("  ", None),
        ("\t\n", None),
        ("  \n", None),
        ("22.10.2026 23:59:59", datetime(2026, 10, 22, 23, 59, 59)),
        ("22.10.2026 00:00:00", datetime(2026, 10, 22, 0, 0, 0)),
        ("22.10.2026 12:00:00", datetime(2026, 10, 22, 12, 0, 0)),
        ("22.10.2026 23:59", datetime(2026, 10, 22, 23, 59)),
        ("22.10.2026 00:00", datetime(2026, 10, 22, 0, 0)),
        ("22.10.2026 12:00", datetime(2026, 10, 22, 12, 0)),
        ("22.10.2026", datetime(2026, 10, 22)),
        ("22.10.2026 12:00  ", datetime(2026, 10, 22, 12, 0)),
        ("  22.10.2026 12:00", datetime(2026, 10, 22, 12, 0)),
        ("string", None),
        ("22/10/2026", None),
        ("22.10.2026 25:00", None),
        ("22.13.2026", None),
        ("22.10.2026 12:00:60", None),
        ("22.10.2026 12:60:00", None),
    ],
)
def test__parse_datetime(value, excepted):
    assert excepted == _parse_datetime(value)


@pytest.mark.parametrize(
    "value, excepted",
    [
        (datetime(2026, 10, 22), datetime(2026, 10, 23, 0, 0, 0, 0)),
        (datetime(2026, 10, 22, 12, 00), datetime(2026, 10, 23, 0, 0, 0, 0)),
        (datetime(2026, 10, 31, 23, 59), datetime(2026, 11, 1, 0, 0, 0, 0)),
    ],
)
def test__start_of_next_day(value, excepted):
    assert excepted == _start_of_next_day(value)


@pytest.mark.parametrize(
    "value, offset, excepted",
    [
        (None, timedelta(0), None),
        ("", timedelta(0), None),
        ("   ", timedelta(0), None),
        (" - ", timedelta(0), None),
        ("-", timedelta(0), None),
        ("15.06.2023", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 16))),
        ("15.06.2023 10:30", timedelta(0), (datetime(2023, 6, 15, 10, 30), datetime(2023, 6, 16))),
        ("15.06.2023 10:30:45", timedelta(0), (datetime(2023, 6, 15, 10, 30, 45), datetime(2023, 6, 16))),
        ("15.06.2023 - 20.06.2023", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 20))),
        (
            "15.06.2023 10:30 - 20.06.2023 18:45",
            timedelta(0),
            (datetime(2023, 6, 15, 10, 30), datetime(2023, 6, 20, 18, 45)),
        ),
        (
            "15.06.2023 10:30:15 - 20.06.2023 18:45:59",
            timedelta(0),
            (datetime(2023, 6, 15, 10, 30, 15), datetime(2023, 6, 20, 18, 45, 59)),
        ),
        ("15.06.2023 - 20.06.2023 18:45", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 20, 18, 45))),
        ("15.06.2023 10:30 - 20.06.2023", timedelta(0), (datetime(2023, 6, 15, 10, 30), datetime(2023, 6, 20))),
        ("  15.06.2023   -   20.06.2023  ", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 20))),
        ("15.06.2023 - 20.06.2023", timedelta(hours=3), (datetime(2023, 6, 14, 21, 0), datetime(2023, 6, 19, 21, 0))),
        ("15.06.2023 - 20.06.2023", timedelta(hours=-5), (datetime(2023, 6, 15, 5, 0), datetime(2023, 6, 20, 5, 0))),
        ("15.06.2023", timedelta(hours=3), (datetime(2023, 6, 14, 21, 0), datetime(2023, 6, 15, 21, 0))),
        (
            "15.06.2023 10:30 - 20.06.2023 18:45",
            timedelta(days=1),
            (datetime(2023, 6, 14, 10, 30), datetime(2023, 6, 19, 18, 45)),
        ),
        ("garbage", timedelta(0), None),
        ("2023-06-15", timedelta(0), None),
        ("garbage - 20.06.2023", timedelta(0), None),
        ("15.06.2023 - garbage", timedelta(0), None),
        ("15.06.2023 - 32.01.2023", timedelta(0), None),
        ("15.06.2023 25:00 - 20.06.2023", timedelta(0), None),
        ("15.06.2023 - 20.06.2023 - 25.06.2023", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 20))),
        ("15.06.2023 - ", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 16))),
        (" - 15.06.2023", timedelta(0), (datetime(2023, 6, 15), datetime(2023, 6, 16))),
        (
            "15.06.2023 08:00 - 15.06.2023 20:00",
            timedelta(0),
            (datetime(2023, 6, 15, 8, 0), datetime(2023, 6, 15, 20, 0)),
        ),
        ("29.02.2024 - 01.03.2024", timedelta(0), (datetime(2024, 2, 29), datetime(2024, 3, 1))),
        (
            "22.10.2026 12:00 - 10.10.2026 13:00",
            timedelta(0),
            (datetime(2026, 10, 10, 13, 0), datetime(2026, 10, 22, 12, 0)),
        ),
    ],
)
def test__parse_bounds(value, offset, excepted):
    assert excepted == _parse_bounds(value, offset)
