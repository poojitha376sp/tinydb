# Decision-experiment variants

Both experiments hold the models, step limits, checks and tasks fixed within an experiment and
change one decision. Results, with links to every run: [results/runs.md](../results/runs.md).
How the runs were started: the workflow's manual inputs (see the main README).

## E1: reviewer independence (ADR-008, result recorded in ADR-014)

Task: review the five seeded PRs in [seeded_prs/](seeded_prs/) (S1 clean, S2 to S5 one seeded
defect each), 2 trials per PR and variant, 20 reviews. Only stage 6 runs, and it only posts a
comment. Correct verdict: S1 APPROVE, S2 to S5 REQUEST_CHANGES.

| | A: `review_variant=baseline` | B: `review_variant=independent` (the design) |
|---|---|---|
| Model | the Builder's family: Google chain (Gemini Flash Lite) | another family: NVIDIA Nemotron 3 Ultra chain |
| Sees | issue, diff, PR checkout, **the PR author's description** | issue, diff, PR checkout only |
| Prompt | `prompts/reviewer_baseline.md`: decide whether to merge | `prompts/reviewer.md`: adversarial, must write and run a break-it test |
| Evidence rules | none: its verdict is taken as given | finish check while working, `judge` afterwards (ADR-014) |
| Step limit | 20 when A ran (it never used more than 12 steps, so the limit never bound) | 40 |

ADR-008 planned to give A the spec and the Builder's transcript. Seeded PRs have neither, so the
PR author's description (written like an ordinary contributor's) plays that role. A and B differ
in a package of choices, not one factor; ADR-014 reports an offline
re-judging of A's reviews under B's rules to separate the effect of the rules.

Pilots, reported but not counted: B on Groq `gpt-oss-120b` (stopped by Groq's daily token
quota) and B on Nemotron with the old 20-step limit (no verdict written in time).

## E2: architecture context for the design stage (ADR-003, result recorded in ADR-016)

Task: stages 1 to 4 (`stop_after=4`, nothing pushed) on copies of issues I1 to I4, opened as
issues #30 to #33 without the `autose` label so only these runs touched them. 1 trial per issue
and variant, 8 runs. Graded with [hidden_tests/](hidden_tests/), applied to each run's diff
outside the repository.

| | `arch_context=full` | `arch_context=map` |
|---|---|---|
| Stage 2 gets | the full `ARCHITECTURE.md` from A2 (108 lines) | `workflow/context/architecture_map.md` (15 lines: components, 4 rules) |
| Everything else | same models, prompts, checks, limits | same |

`ARCHITECTURE.md` is excluded from every build sandbox, so the map variant really sees only the
map. After E2 the map became the default (ADR-016).
