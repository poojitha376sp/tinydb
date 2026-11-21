import pytest
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

def test_ac_fr001_a_raises_value_error_if_source_does_not_exist():
    db = TinyDB(storage=MemoryStorage)
    with pytest.raises(ValueError):
        db.rename_table('nonexistent', 'users')

def test_ac_fr001_b_raises_value_error_if_destination_already_exists():
    db = TinyDB(storage=MemoryStorage)
    db.table('usr').insert({'data': 1})
    db.table('existing_table').insert({'data': 2})
    
    with pytest.raises(ValueError):
        db.rename_table('usr', 'existing_table')

def test_ac_fr001_c_preserves_documents_and_ids():
    db = TinyDB(storage=MemoryStorage)
    table_usr = db.table('usr')
    table_usr.insert({'name': 'John', 'age': 30})
    
    # Capture the doc_id and data
    doc = table_usr.all()[0]
    doc_id = doc.doc_id
    
    db.rename_table('usr', 'users')
    
    table_users = db.table('users')
    assert len(table_users) == 1
    new_doc = table_users.get(doc_id=doc_id)
    assert new_doc is not None
    assert new_doc['name'] == 'John'
    assert new_doc.doc_id == doc_id

def test_ac_fr001_d_removes_old_table_from_list():
    db = TinyDB(storage=MemoryStorage)
    db.table('usr').insert({'data': 1})
    
    assert 'usr' in db.tables()
    
    db.rename_table('usr', 'users')
    
    assert 'usr' not in db.tables()
    assert 'users' in db.tables()

def test_ac_nfr001_a_storage_remains_unchanged_on_failure():
    # AC-NFR001-a: db.rename_table('nonexistent', 'users') -> storage data remains unchanged
    # This verifies that if validation fails, the storage state is not modified.
    db = TinyDB(storage=MemoryStorage)
    
    # Insert some data in an existing table to ensure state is kept
    db.table('keep').insert({'val': 'preserve'})
    
    with pytest.raises(ValueError):
        db.rename_table('nonexistent', 'users')
        
    assert 'keep' in db.tables()
    assert db.table('keep').all()[0]['val'] == 'preserve'
    assert 'users' not in db.tables()
