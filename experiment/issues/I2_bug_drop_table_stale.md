Type: bug report

Title: Table still returns old documents after `drop_table`

In my app I keep a reference to a table object and reuse it (`users = db.table('users')`). When I reset the data with `db.drop_table('users')`, searches through that same object still return the deleted documents, even though `len()` says the table is empty:

```python
from tinydb import TinyDB, where
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
users = db.table('users')
users.insert({'name': 'ann'})
print(users.search(where('name') == 'ann'))   # [{'name': 'ann'}]

db.drop_table('users')

print(len(users))                              # 0  (correct)
print(users.search(where('name') == 'ann'))   # [{'name': 'ann'}]  <- should be []
print(users.count(where('name') == 'ann'))    # 1                  <- should be 0
```

The same thing happens with `db.drop_tables()`. It only goes away if I call `users.clear_cache()` myself, which I didn't know I had to do. I would expect a dropped table to behave like an empty table.

TinyDB 4.9.0, Python 3.10.
