from tinydb import TinyDB, Query, where
from tinydb.storages import MemoryStorage

def test_ac_fr001_a_drop_table_clears_cache():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    
    # Pre-check: data exists
    assert len(users.search(where('name') == 'ann')) == 1
    
    db.drop_table('users')
    
    # AC-FR001-a: should be [] after drop
    assert users.search(where('name') == 'ann') == []

def test_ac_fr002_a_drop_tables_clears_cache():
    db = TinyDB(storage=MemoryStorage)
    users = db.table('users')
    users.insert({'name': 'ann'})
    
    # Pre-check: data exists
    assert len(users.search(where('name') == 'ann')) == 1
    
    db.drop_tables()
    
    # AC-FR002-a: should be [] after drop_tables
    assert users.search(where('name') == 'ann') == []
