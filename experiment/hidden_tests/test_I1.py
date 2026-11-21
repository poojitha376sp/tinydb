"""Hidden acceptance tests for I1: fragment() on a field must not share cache with another field."""
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'a', 'home': {'wifi': True}})
    db.insert({'name': 'b', 'work': {'wifi': True}})
    return db


def test_second_field_fragment_not_served_from_first_fields_cache():
    db = _db()
    assert [d['name'] for d in db.search(Query().home.fragment({'wifi': True}))] == ['a']
    assert [d['name'] for d in db.search(Query().work.fragment({'wifi': True}))] == ['b']


def test_fragment_queries_on_different_paths_are_not_equal():
    assert Query().home.fragment({'wifi': True}) != Query().work.fragment({'wifi': True})


def test_root_and_field_fragment_are_distinct():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'wifi': True})
    db.insert({'home': {'wifi': True}})
    assert len(db.search(Query().fragment({'wifi': True}))) == 1
    assert [d.doc_id for d in db.search(Query().home.fragment({'wifi': True}))] == [2]
