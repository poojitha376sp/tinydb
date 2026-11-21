"""Hidden acceptance tests for I4: Query().field.between(low, high), inclusive."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    for age in (17, 18, 25, 30, 31):
        db.insert({'age': age})
    db.insert({'name': 'no age'})
    db.insert({'age': 'twenty'})
    return db


def test_bounds_are_inclusive():
    db = _db()
    assert sorted(d['age'] for d in db.search(Query().age.between(18, 30))) == [18, 25, 30]


def test_missing_or_incomparable_values_do_not_match_or_raise():
    db = _db()
    res = db.search(Query().age.between(0, 100))
    assert sorted(d['age'] for d in res) == [17, 18, 25, 30, 31]


def test_different_bounds_are_not_served_from_the_same_cache_entry():
    db = _db()
    assert len(db.search(Query().age.between(18, 30))) == 3
    assert len(db.search(Query().age.between(18, 25))) == 2
