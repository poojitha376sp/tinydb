"""Hidden acceptance tests for I3: TinyDB.rename_table(old, new)."""
import pytest

from tinydb import TinyDB
from tinydb.storages import MemoryStorage


def _db():
    db = TinyDB(storage=MemoryStorage)
    usr = db.table('usr')
    usr.insert({'name': 'ann'})
    usr.insert({'name': 'bob'})
    return db


def test_rename_moves_documents_and_ids():
    db = _db()
    db.rename_table('usr', 'users')
    docs = db.table('users').all()
    assert [(d.doc_id, d['name']) for d in docs] == [(1, 'ann'), (2, 'bob')]


def test_old_name_is_gone():
    db = _db()
    db.rename_table('usr', 'users')
    assert 'usr' not in db.tables()
    assert 'users' in db.tables()


def test_missing_source_raises_value_error():
    db = _db()
    with pytest.raises(ValueError):
        db.rename_table('nope', 'users')


def test_existing_target_raises_and_keeps_data():
    db = _db()
    db.table('users').insert({'name': 'zed'})
    with pytest.raises(ValueError):
        db.rename_table('usr', 'users')
    assert len(db.table('usr')) == 2
    assert [d['name'] for d in db.table('users').all()] == ['zed']
