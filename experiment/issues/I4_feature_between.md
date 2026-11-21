Type: feature request

Title: Range query helper (`between`)

I do a lot of range searches like "age from 18 to 30" and always write

```python
db.search((User.age >= 18) & (User.age <= 30))
```

It would be nice to have a shortcut:

```python
db.search(User.age.between(18, 30))
```

Both ends should be included (18 and 30 match). Documents that don't have the field, or where the value can't be compared (e.g. a string when I pass numbers), should simply not match instead of raising an error.
