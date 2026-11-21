Type: bug report

Title: `fragment()` on a field returns results from a different field

Hi! I think I found a caching problem with `fragment`. I'm using the "search for documents where a specific field matches the fragment" feature from the docs (`Query().field.fragment(...)`).

I have two kinds of documents, one with the settings under `home` and one under `work`:

```python
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

db = TinyDB(storage=MemoryStorage)
db.insert({'name': 'a', 'home': {'wifi': True}})
db.insert({'name': 'b', 'work': {'wifi': True}})

print(db.search(Query().home.fragment({'wifi': True})))
print(db.search(Query().work.fragment({'wifi': True})))
```

Expected:
```
[{'name': 'a', 'home': {'wifi': True}}]
[{'name': 'b', 'work': {'wifi': True}}]
```

Actual:
```
[{'name': 'a', 'home': {'wifi': True}}]
[{'name': 'a', 'home': {'wifi': True}}]
```

The second search gives me the result of the first one. If I call `db.clear_cache()` between the two searches, the second one is correct, so it looks like both queries end up in the same cache slot. Same thing happens with a JSON file database.

TinyDB 4.9.0, Python 3.10.
