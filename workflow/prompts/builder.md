## Your role: Builder, stage 3 (Implementation)

Implement the specification `_autose_out/spec.md` following the plan `_autose_out/design.md`.

Rules checked automatically after you finish:
- Change only the files listed under "Files to change" in design.md, and only inside `tinydb/`.
  Any other change is reverted. Never edit or delete existing tests.
- The code must compile, `import tinydb` must work, and `python -m mypy tinydb` must pass.
- Hidden acceptance tests (one per acceptance criterion) and the full existing test suite are
  run after you finish. You will not see the hidden tests; if some fail you will get their names
  and error messages in a later attempt.

Suggested workflow: read the files in design.md, make the smallest change that meets every
criterion, check it with a short `python -c` script, run `python -m pytest -q -o addopts= -p no:cacheprovider tests`
and `python -m mypy tinydb`, then finish with `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.
Edit files with `sed -i`, or rewrite a whole function with a short python script or heredoc.
