## Your role: Analyst, stage 1 (Requirements)

Turn the GitHub issue into a specification, `_autose_out/spec.md`.

1. Read the skill first: `cat _autose_skill/SKILL.md`. Follow it. This run is NON-INTERACTIVE:
   nobody can answer questions, so log every question as an OQ- and continue, as the skill says.
2. Look at the code only as much as needed to state requirements precisely
   (e.g. `grep -n "def fragment" -A20 tinydb/queries.py`). Do not design or implement anything.
3. Write the spec with a heredoc, for example `cat <<'EOF' > _autose_out/spec.md` ... `EOF`.

The spec must follow the skill, and must also contain these machine-checked lines:

- One verdict line exactly like: `Verdict: IMPLEMENTATION-READY` (or `PARTIALLY-READY`, `NOT-READY`),
  decided by the skill's readiness rule. Use NOT-READY when the work cannot start without a
  person's answer. A vague issue may still be PARTIALLY-READY if a clear, small subset can proceed.
- Requirement records as in the skill (`ID: FR-001` with `Statement: The system SHALL ...`).
- A final section `## Acceptance criteria (machine-checkable)` with one line per criterion:
  `AC-FR001-a: <exact setup or call> -> <exact observable result>`
  Each must be checkable by one automated test: name the function or method, the input and the
  expected return value, exception type or stored data. No vague words (better, easy, fast,
  properly, appropriate, nice, robust, efficient, etc).
- Every FR needs at least one AC line. Keep the scope to what the issue asks; 2 to 6 ACs is typical.

When `_autose_out/spec.md` is written, check it with `cat _autose_out/spec.md`, then finish with
`echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.
