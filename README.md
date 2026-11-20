# AutoSE A3: issue in, independently reviewed pull request out

This is a fork of [TinyDB](https://github.com/msiemens/tinydb) with a GitHub Actions workflow
that takes a GitHub issue through six fixed stages and ends with a tested pull request and an
independent review. A person always makes the final merge decision.

The original TinyDB readme is in [README.rst](README.rst).

| | |
|---|---|
| Fork | https://github.com/poojitha376sp/tinydb |
| Base commit (all runs start here) | `edff96a` on `master` (upstream TinyDB, unchanged code) |
| Workflow | [.github/workflows/autose.yml](.github/workflows/autose.yml), copy in [workflow/workflows/](workflow/workflows/) |
| Agent code | [workflow/autose/](workflow/autose/) |
| Prompts | [workflow/prompts/](workflow/prompts/) |
| Design | [architecture/views/](architecture/views/), [architecture/decisions/](architecture/decisions/) (ADR-001 to ADR-010) |
| Experiments | [experiment/](experiment/) |
| Results | [results/results.csv](results/results.csv), [results/runs.md](results/runs.md) |
| Report | [report.pdf](report.pdf) |
| Demo video | (link added after the final run) |

## How it works

```
issue labelled "autose"
  -> 1 Requirements  Analyst agent writes spec.md          check: spec gate (SHALL, ACs, no vague words)
  -> 2 Design        Analyst agent writes design.md        check: every planned file and symbol exists
  -> 4a Tests        Test Author writes acceptance tests   check: every new test FAILS on the base code
  -> 3 Implement     Builder changes tinydb/*.py           check: compiles, imports, mypy, stays in plan
  -> 4b Testing      plain code runs the whole suite       check: new tests pass, no old test breaks
                     (fail -> back to 3, at most 3 tries; same failure twice -> back to 2, once)
  -> 5 Release       plain code pushes autose/issue-N, opens the PR, runs the project CI
  -> 6 Review        Reviewer agent (different model family, sees no Builder reasoning)
                     APPROVE -> label ready-for-human
                     REQUEST_CHANGES -> one more round from stage 2 or 3, then needs-human
```

Four agents (Analyst, Test Author, Builder, Reviewer) run on
[mini-swe-agent](https://github.com/SWE-agent/mini-swe-agent). The control flow between them is
plain Python ([orchestrator.py](workflow/autose/orchestrator.py)), not an agent. Every stage
uploads its artifacts (spec, design, tests, diff, test report, trajectories,
`stage_results.json`) to the Actions run, and the issue gets one status comment that is updated
as the run goes.

Safety in short (details in ADR-005 and ADR-009): agents never hold a GitHub token; they run as
a separate unprivileged Linux user with an empty environment; every command passes an allowlist
per role; files a role may not change are reverted; the Builder never sees the acceptance tests;
the issue text is wrapped as untrusted data; the run stops at a token cap.

## Models (all free tiers)

| Role | Model | Where the key comes from |
|---|---|---|
| Analyst, Test Author, Builder | Gemini chain: `gemini-3-flash-preview`, `gemini-3.5-flash`, `gemini-3.8-flash`, `gemini-3.1-flash-lite` (a busy model hands over to the next) | Google AI Studio key, secret `GEMINI_API_KEY` |
| Reviewer | `openai/gpt-4.1-mini` through GitHub Models | the workflow's own `GITHUB_TOKEN` (`models: read`) |
| Reviewer fallback | `groq/llama-3.3-70b-versatile` | Groq key, secret `GROQ_API_KEY` (optional) |

The Reviewer is from a different model family than the Builder on purpose (ADR-006, ADR-008).
Models can be changed without code changes through the repository variables
`AUTOSE_BUILD_MODELS` and `AUTOSE_REVIEW_MODELS` (comma separated fallback chains).

## How to trigger the workflow

1. Open an issue in this repository describing a bug or a small feature.
2. Add the label `autose` to it (or, as a collaborator, comment `/autose` on it).
3. Watch the run under the Actions tab. The issue's status comment links to the run, and the
   pull request appears as `autose/issue-<number>`.

Experiments use **Actions -> autose -> Run workflow** with inputs:
- E1 (reviewer independence): `review_pr` = a seeded PR number, `review_variant` =
  `independent` or `baseline`. Only stage 6 runs and it only posts a comment.
- E2 (architecture context): `arch_context` = `full` or `map`, `stop_after` = `4`. Stages 1 to 4
  run and nothing is pushed.

## Setup for your own copy

1. Fork, then add the repository secret `GEMINI_API_KEY` (and optionally `GROQ_API_KEY`).
2. Settings -> Actions -> General -> Workflow permissions: allow GitHub Actions to create pull requests.
3. Protect `master` so the workflow can never push to it.

## Running the harness checks locally

No keys and no network needed; the model is replaced by a fixed script.

```
cd workflow
pip install -r requirements.txt
python -m pytest -q -o addopts= selftest/check_harness.py selftest/check_pipeline.py
```

## AI use

Following the course policy: I used Claude Code (Anthropic) as a coding assistant while building
the workflow code, the self-tests and the experiment materials. The architecture decisions
(ADRs) are my own. I reviewed what the assistant produced before committing it.
