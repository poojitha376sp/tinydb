# TinyDB map (experiment E2, variant "map": a short map instead of the full ARCHITECTURE.md)

Components (all in `tinydb/`):
- `database.py` TinyDB: creates the storage, hands out Table objects (kept in `_tables`), forwards unknown attributes to the default table.
- `table.py` Table: all document operations; owns the per-table query cache.
- `queries.py` Query / QueryInstance: builds query callables; each carries a hash value.
- `storages.py` Storage, JSONStorage, MemoryStorage: read/write the whole database dict.
- `middlewares.py` Middleware, CachingMiddleware: wrap a storage class.
- `utils.py` LRUCache, FrozenDict, freeze. `operations.py` update helpers.

Rules:
1. Table code changes data only through `Table._update_table` (read whole db, change, write, clear cache).
2. A query's hash must identify the query completely: operator, path and every argument (frozen with `freeze`).
3. Imports point one way: queries/storages/utils never import table or database.
4. New storages subclass Storage and implement read/write; middlewares take a storage class.
