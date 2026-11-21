# Component view

The agents, their tools, and how they call each other, as built and run. Decisions referenced:
ADR-001 (agents), ADR-002 (control flow), ADR-003 (hand-offs), ADR-004 (state), ADR-011 (tools,
sandbox and credentials, superseding ADR-005), ADR-012 (models, superseding ADR-006), ADR-008 and
ADR-014 (reviewer), ADR-015 (action parsing), ADR-016 (design context).

```mermaid
flowchart TB
    subgraph GH[GitHub: poojitha376sp/tinydb]
        ISS[Issue + status comment<br/>autose-state JSON]
        PR[Pull request]
        CI[CI workflow<br/>ci-workflow.yml]
        ART[(Workflow artifacts<br/>spec, design, tests, diff,<br/>test_report, pr, review,<br/>trajectories, stage_results)]
    end

    subgraph J1[Job orchestrate: contents, pull-requests, issues, actions write]
        ORC[Orchestrator<br/>plain Python state machine<br/>no LLM]
        GATE[Gate checks<br/>spec parser, AST lookup,<br/>mypy + pycodestyle, pytest red-green,<br/>path guard and revert]
        REL[Release code<br/>gh: push branch, PR, dispatch CI]
        subgraph SBX[Sandbox: Linux user autose-agent, empty env, no token]
            AN[Analyst<br/>stages 1-2]
            TA[Test Author<br/>stage 4a, one repair]
            BU[Builder<br/>stage 3]
        end
        HAR[Harness<br/>per-role allowlist,<br/>one-action parser,<br/>required output files]
    end

    subgraph J2[Job review-run: contents, issues, pull-requests read]
        RV[Reviewer<br/>stage 6, harness from master,<br/>PR head checked out as data]
        JD[judge<br/>evidence rules]
    end

    subgraph J3[Job review-post: pull-requests, issues, actions write; no agent]
        RP[post_review<br/>comment, labels, next round]
    end

    GEM[[Google chain<br/>gemini-3.5 / 3.1 flash-lite ... gemma]]
    ALT[[Other families<br/>NVIDIA Nemotron 3 Ultra, Mistral Large 4,<br/>MiniMax M3.1 Flash, Groq gpt-oss]]

    ISS -- label autose or /autose --> ORC
    ORC -- issue text as untrusted data --> AN
    AN -- spec.md, design.md --> GATE
    ORC -- spec.md only --> TA
    TA -- new tests --> GATE
    ORC -- spec.md, design.md,<br/>failing test names and errors --> BU
    BU -- code edits --> GATE
    AN & TA & BU -- every command --> HAR
    GATE -- pass / fail --> ORC
    ORC --> REL
    REL --> PR
    REL -- workflow_dispatch --> CI
    ORC -- state + links --> ISS
    ORC -- uploads --> ART
    AN & TA & BU -. LLM calls .-> GEM
    PR -- issue, diff, PR head --> RV
    RV -. LLM calls .-> ALT
    RV -- review.json + command history --> JD
    JD -- review_result.json --> RP
    RP -- review comment, label --> PR
    RP -- changes requested: workflow_dispatch<br/>resume at stage 2 or 3 --> ORC
```

## Agents and tools

| Agent | Stages | Tools (allowlist) | Model | Receives | Never receives |
|---|---|---|---|---|---|
| Analyst | 1 Requirements, 2 Design | read-only file commands | Google chain | issue text (wrapped as untrusted), A1 skill, the short architecture map, base code | Builder output, tests |
| Test Author | 4a, plus one repair | read; write its one test file; pytest | Google chain | spec.md, base code; for a repair, only the failure messages | design.md, Builder's code and reasoning |
| Builder | 3 | read; edit inside `tinydb/`; python, pytest, mypy, pycodestyle | Google chain | spec.md, design.md, base code, failing test names and errors | test source code, ARCHITECTURE.md |
| Reviewer | 6 | read and run in a throwaway checkout; write `_review/` scratch tests | other family (NVIDIA chain) | issue, diff, PR head, ARCHITECTURE.md | spec.md, design.md, test_report.md, transcripts, PR description |

Plain code, not agents: the Orchestrator (stage routing), every gate check, the Release code
(stage 5), the review `judge` and `post_review`. Only plain code holds a GitHub token. `git`,
the network, `pip` and `env` are blocked for every agent. The workflow never merges; a person does.
