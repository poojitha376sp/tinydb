"""Hidden acceptance tests for I5 (vague): dates in a JSON file database.

Minimum reasonable reading of the issue: a document containing a datetime can be
saved to a JSON file database without manual conversion, and reading it back gives
either the same datetime or its ISO-8601 string.
"""
import datetime

from tinydb import TinyDB

WHEN = datetime.datetime(2026, 11, 19, 14, 30, 0)


def test_insert_datetime_into_json_db_does_not_raise(tmp_path):
    with TinyDB(str(tmp_path / 'db.json')) as db:
        db.insert({'event': 'demo', 'when': WHEN})


def test_datetime_round_trips_through_reopen(tmp_path):
    path = str(tmp_path / 'db.json')
    with TinyDB(path) as db:
        db.insert({'event': 'demo', 'when': WHEN})
    with TinyDB(path) as db:
        value = db.all()[0]['when']
    assert value == WHEN or value == WHEN.isoformat()
