"""Hidden acceptance tests for I2: a held table reference must not return dropped documents."""
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage


def _setup():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    assert users.search(where('name') == 'ann')  # fills the query cache
    return db, users


def test_search_after_drop_table_is_empty():
    db, users = _setup()
    db.drop_table('users')
    assert users.search(where('name') == 'ann') == []


def test_count_after_drop_table_is_zero():
    db, users = _setup()
    db.drop_table('users')
    assert users.count(where('name') == 'ann') == 0


def test_search_after_drop_tables_is_empty():
    db, users = _setup()
    db.drop_tables()
    assert users.search(where('name') == 'ann') == []
