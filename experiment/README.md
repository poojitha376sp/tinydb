# Experiment materials

Base for everything: TinyDB `edff96a` (upstream code, unchanged). Nothing was planted in the
base code: every issue describes real behaviour of that commit, found by reading the source and
reproducing it. These files were kept outside the repository until all agent runs were done,
and the agents' sandboxes exclude this folder (`SANDBOX_EXCLUDE` in `workflow/autose/config.py`).
`conftest.py` keeps pytest from collecting anything here.

| Folder | What |
|---|---|
| [issues/](issues/) | the five issue texts as posted (I1 #3, I2 #9, I3 #10, I4 #14, I5 #18) |
| [hidden_tests/](hidden_tests/) | 2 to 4 acceptance tests per issue, never shown to any agent |
| [reference_fixes/](reference_fixes/) | a minimal fix per issue, used only to prove each hidden test can pass |
| [seeded_prs/](seeded_prs/) | the five E1 PRs (S1 clean, S2 to S5 with one seeded defect), their labels and ground-truth checks |
| [variants.md](variants.md) | what each variant of E1 and E2 changes |

| Issue | Type | Real behaviour at `edff96a` | Hidden tests | On base | With reference fix |
|---|---|---|---|---|---|
| I1 | bug | `fragment()` hash ignores the field path, so `Query().home.fragment(x)` and `Query().work.fragment(x)` share a cache entry | 3 | 3 fail | 3 pass |
| I2 | bug | `drop_table` / `drop_tables` do not clear the query cache of table objects the caller still holds | 3 | 3 fail | 3 pass |
| I3 | feature | no way to rename a table | 4 | 4 fail | 4 pass |
| I4 | feature | no range query | 3 | 3 fail | 3 pass |
| I5 | vague | "better support for dates" (a datetime makes the JSON storage raise) | 2 | 2 fail | 2 pass |

To grade a run: copy `tinydb/` and `tests/` from `edff96a` to a scratch folder, apply the run's
`diff.patch`, copy `hidden_tests/test_IN.py` into `tests/`, and run
`python -m pytest -q -o addopts= tests/test_IN.py`. E1 and E2 issue and PR numbers:
seeded issues #20, 22, 24, 26, 28 with PRs #21, 23, 25, 27, 29; E2 issue copies #30 to #33.
