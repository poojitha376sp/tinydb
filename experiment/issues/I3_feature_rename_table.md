Type: feature request

Title: Add a way to rename a table

I named a table badly early on (`'usr'`) and now want it to be called `'users'`. Right now the only way I found is to copy every document into a new table and then drop the old one, which is clumsy and loses the document IDs unless I'm careful.

It would be great to have something like:

```python
db.rename_table('usr', 'users')
```

After that, `db.table('users')` should have exactly the documents (and doc IDs) that `'usr'` had, and `'usr'` should no longer show up in `db.tables()`.

If the old table doesn't exist, or a table with the new name already exists, I'd expect it to refuse with a `ValueError` (like other TinyDB argument errors) and not touch any data.
