# Sequence view (a real run)

Issue I3, [#10](https://github.com/poojitha376sp/tinydb/issues/10) ("rename a table"), third
run: [44874308479](https://github.com/poojitha376sp/tinydb/actions/runs/44874308479). It ended
with [PR #19](https://github.com/poojitha376sp/tinydb/pull/19), green CI
([44874520635](https://github.com/poojitha376sp/tinydb/actions/runs/44874520635)) and an
independent APPROVE. Seconds, steps and tokens are copied from the run's `stage_results.json`
and `review_result.json` (`results/results.csv` has the same numbers). The code later passed
all 4 hidden tests.

```mermaid
sequenceDiagram
    autonumber
    actor M as Maintainer
    participant GH as GitHub (issue, PR, CI)
    participant O as Orchestrator (plain code)
    participant A as Analyst (Gemini)
    participant T as Test Author (Gemini)
    participant B as Builder (Gemini)
    participant R as Reviewer (other family)
    participant P as review-post (plain code)

    M->>GH: label issue #10 "autose"
    GH->>O: workflow run 44874308479 (gate: sender is a User)
    O->>GH: status comment "running" (autose-state JSON)
    O->>A: issue text as untrusted data + A1 skill
    A-->>O: spec.md (3 steps, 7 s)
    O->>O: check_spec: 4 ACs, IMPLEMENTATION-READY
    O->>A: spec.md + architecture context
    A-->>O: design.md (19 steps, 30 s, model switch on rate limit)
    O->>O: check_design: plans tinydb/database.py, symbols exist
    O->>T: spec.md only
    T-->>O: tests/test_autose_issue10.py (8 steps, 37 s)
    O->>O: check_red: 5 new tests, all fail on base
    O->>B: spec.md + design.md (no test code)
    B-->>O: edits to tinydb/database.py (17 steps, 34 s)
    O->>O: check_build: compiles, imports, mypy, in plan
    O->>O: 4b check_green: 233/233 tests pass (first attempt)
    O->>GH: push autose/issue-10, open PR #19 (pr.md: AC -> test -> file)
    O->>GH: dispatch CI on the PR commit, wait: success (106 s for stage 5)
    GH->>R: job review-run: issue, diff, PR head (harness from master)
    R->>R: runs the suite, writes and runs _review break-it tests
    R->>R: review.json APPROVE (19 steps, average score 9.0)
    R->>R: judge (plain code): break-it test really ran, no must-fix finding
    R->>P: review_result.json (artifact)
    P->>GH: review comment on PR #19, label ready-for-human
    GH-->>M: a person decides whether to merge
```

Build stages total 290K tokens (Analyst 128K, Test Author 36K, Builder 126K); the review used
77K. At the time of this run the Reviewer was `gpt-oss-120b` on Groq; it later moved to NVIDIA
(ADR-012).

What does not show in this happy path, and where to see it:
- Stage 4b failing and going back to 3, or the same failure twice (ADR-002, ADR-013): I3's two
  earlier runs, 44790279547 and 44819950934, in `results/runs.md`.
- Stage 1 stopping on NOT-READY with open questions for a person: I5,
  [44874333544](https://github.com/poojitha376sp/tinydb/actions/runs/44874333544).
- A review that ends INCONCLUSIVE and is labelled `needs-human`: the PR #15 reviews.
