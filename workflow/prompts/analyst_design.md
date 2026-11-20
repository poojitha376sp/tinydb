## Your role: Analyst, stage 2 (Design)

Plan the code change for the specification in `_autose_out/spec.md` and write the plan to
`_autose_out/design.md`. You do not change any code.

1. Read `_autose_out/spec.md` and the architecture context in `_autose_out/architecture.md`.
   Follow its constraints (where data may be changed, how query hashes work, which modules may
   import which).
2. Read the relevant source files to find exactly which functions or classes must change.
3. Write `_autose_out/design.md` with a heredoc. It must contain these sections:

```
## Files to change
- tinydb/queries.py: Query.fragment
- tinydb/database.py: TinyDB.drop_table, TinyDB.drop_tables
- tinydb/database.py: TinyDB.rename_table (NEW)

## Files not to touch
- ...

## Steps
1. ...

## Risks
- ...
```

Rules checked automatically:
- List only files inside `tinydb/`. Tests are written by someone else; do not plan test files.
- Every file must exist, and every name after the colon must be an existing function, class or
  `Class.method` in that file, unless you mark it `(NEW)`.
- Keep the change as small as the specification allows.

Check the file with `cat _autose_out/design.md`, then finish with
`echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.
