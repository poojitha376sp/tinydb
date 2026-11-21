# Stage map

Who does each stage, what it reads, what it must produce, and the check that decides whether
the next stage may start. Every check is plain code (no LLM judges another LLM's work here),
except stage 6, which is the independent Reviewer. Decisions referenced: ADR-002 (control
flow), ADR-003 (hand-offs), ADR-011 (tools), ADR-007 (checks), ADR-009 (failures), ADR-013
(test repair), ADR-014 (reviewer evidence), ADR-016 (design context).

| Stage | Done by | Reads | Writes (artifact) | May change | Check (code) | If the check fails |
|---|---|---|---|---|---|---|
| 1 Requirements | Analyst agent | issue text (wrapped as untrusted), requirements-spec-builder skill | `spec.md` | `_autose_out/` only | `check_spec`: verdict line, every `FR` has a `SHALL` statement and at least one `AC-FRnnn-x: given -> expected`, no vague words | retry once with the problems listed; verdict NOT-READY or second failure: stop, label `autose-failed` |
| 2 Design | Analyst agent | `spec.md`, the short architecture map (default since E2; full `ARCHITECTURE.md` on request), base code read-only | `design.md` | `_autose_out/` only | `check_design`: a `## Files to change` list; every file exists under `tinydb/`; every named class / function exists (AST lookup) unless marked `(NEW)` | retry once; then stop |
| 4a Tests | Test Author agent | `spec.md` only (no design, no code plan) | `tests/test_autose_issueN.py` | that one file | `check_red`: one test per AC (name contains `ac_frnnn_x`), every new test **fails** on the base code | retry once; then stop |
| 3 Implementation | Builder agent | `spec.md`, `design.md`, feedback from the last attempt (failing test names and messages only, never the test code) | `diff.patch` | `tinydb/*.py` only; anything else is reverted | `check_build`: compiles, `import tinydb` works, `mypy tinydb` clean, touched files are inside the plan | counts as a failed attempt, goes back to 3 |
| 4b Testing | plain code | builder tree + the Test Author's acceptance tests (which the Builder never sees) | `test_report.md` | nothing | `check_green`: every new test passes and the full existing suite still passes | back to 3 with feedback (at most 3 attempts in total); the same failure twice: the Test Author may correct its tests once, seeing only the error messages (still red on base); then back to 2 once with "change the plan"; out of attempts: stop |
| 5 Release | plain code | builder tree, tests, spec | branch `autose/issue-N`, PR (`pr.md` with AC -> test -> file table), CI run | the branch only (`master` is protected) | project CI (`ci-workflow.yml`: pytest + mypy) green on the pushed commit | PR stays open, run stops, label `autose-failed` |
| 6 Review | Reviewer agent (other model family), then plain code posts | the issue, a checkout of the PR head (its diff against `master`), `ARCHITECTURE.md`; **not** spec, design, test report, the Builder's reasoning or the PR description | `review.json` -> `review_result.json`, `review.md`, PR comment | `_review/` scratch files only, in a throwaway checkout | `judge`: a finding counts only if its file and line exist and its evidence command was really run; APPROVE needs a break-it test that ran, no must-fix finding and an average score of 7 or more, else INCONCLUSIVE | REQUEST_CHANGES (approach) -> new run from stage 2; (code) -> new run from stage 3; at most 2 review rounds, then `needs-human`. APPROVE -> `ready-for-human` |

Limits (in `workflow/autose/config.py`): build attempts 3, design escalations 1, tries per
agent stage 2, test repairs 1, review rounds 2, agent steps 25 / 25 / 35 / 40 (Analyst / Test
Author / Builder / Reviewer; outputs count down the last 5 steps), command timeout 120 s, token cap 3,000,000 per run, CI wait 30 minutes.

Every stage also writes its status, attempts, seconds, tokens and blocked commands into
`stage_results.json`, and its full agent trajectory into `trajectories/`.
