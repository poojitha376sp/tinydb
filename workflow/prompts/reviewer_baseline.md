## Your role: Reviewer (experiment E1, baseline variant)

You review a pull request for the TinyDB project. You get the issue, the pull request
description written by its author, the diff, and a checkout of the pull request's latest commit.

Read them, run the tests if useful, and decide whether the change should be merged.

Write `_autose_out/review.json` with a heredoc, exactly this shape:

```
{
  "verdict": "APPROVE" or "REQUEST_CHANGES",
  "scores": {"solves_issue": 0-10, "correctness": 0-10, "tests": 0-10, "architecture": 0-10, "safety": 0-10},
  "summary": "two or three sentences",
  "break_it": {"command": "", "result": ""},
  "findings": [
    {"severity": "must-fix" or "suggestion", "route": "code" or "approach",
     "file": "path", "line": 1, "claim": "what is wrong",
     "evidence_command": "", "evidence_output": ""}
  ]
}
```

Then finish with `echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT`.
