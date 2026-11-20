from tinydb import Query, TinyDB
from tinydb.storages import MemoryStorage

def test_ac_fr001_a():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'name': 'a', 'home': {'wifi': True}})
    db.insert({'name': 'b', 'work': {'wifi': True}})
    res1 = db.search(Query().home.fragment({'wifi': True}))
    res2 = db.search(Query().work.fragment({'wifi': True}))
    assert res1 != res2 and res2 == [{'name': 'b', 'work': {'wifi': True}}]
