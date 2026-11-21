"""Ground-truth checks used to LABEL the seeded reviewer PRs. Never shown to any agent.

Each check targets one seeded PR's claim. Run against a tree with the PR applied.
"""
from tinydb import TinyDB, Query, where
from tinydb.storages import MemoryStorage
from tinydb.utils import freeze, FrozenDict


def _db(*docs):
    db = TinyDB(storage=MemoryStorage)
    for d in docs:
        db.insert(d)
    return db


# S1: update_multiple with generators and unique IDs
def test_s1_generator_updates_every_matching_document():
    db = _db({'n': 1}, {'n': 2})
    db.update_multiple((({'hit': True}, where('n') == n) for n in (1, 2)))
    assert db.count(where('hit') == True) == 2  # noqa: E712


def test_s1_ids_are_unique():
    db = _db({'n': 1})
    assert db.update_multiple([({'p': 1}, where('n') == 1), ({'q': 1}, where('n') == 1)]) == [1]


# S2 / S5-free: one_of must work with generators AND with unhashable items (worked before)
def test_s2_one_of_generator():
    db = _db({'c': 'b'}, {'c': 'a'})
    assert len(db.search(where('c').one_of(x for x in ['a', 'b']))) == 2


def test_s2_one_of_unhashable_items_still_work():
    db = _db({'k': [1, 2]}, {'k': [3]})
    assert len(db.search(where('k').one_of([[1, 2], [9]]))) == 1


# S3: freeze must still freeze nested values; list vs tuple must not collide
def test_s3_nested_values_are_frozen():
    frozen = freeze([{'a': [1, 2]}])
    nested = [el for el in frozen if isinstance(el, dict)]
    assert nested and isinstance(nested[0], FrozenDict)


def test_s3_list_tuple_no_collision():
    db = _db({'t': [1, 2]})
    assert len(db.search(where('t') == [1, 2])) == 1
    assert len(db.search(where('t') == (1, 2))) == 0


# S4: a failing callable update leaves documents unchanged
def test_s4_failed_update_is_atomic():
    from tinydb.operations import delete
    db = _db({'x': 1, 'k': 1}, {'k': 1})
    try:
        db.update(delete('x'))
    except KeyError:
        pass
    assert db.all() == [{'x': 1, 'k': 1}, {'k': 1}]


# S5: list/tuple must not collide when nested inside the compared value either
def test_s5_nested_list_tuple_no_collision():
    db = _db({'d': {'a': [1]}})
    assert len(db.search(where('d') == {'a': [1]})) == 1
    assert len(db.search(where('d') == {'a': (1,)})) == 0
