"""Run state kept in one status comment on the issue (ADR-004).

The comment has a human-readable part and a hidden JSON block:
``<!-- autose-state {...} -->``. It is the single source of truth between
stages, review rounds and restarts.
"""
import json
import re
from dataclasses import asdict, dataclass, field

from . import gh

MARK = 'autose-state'
STATE_RE = re.compile(r'<!--\s*autose-state\s*(\{.*?\})\s*-->', re.S)


@dataclass
class RunState:
    issue: int
    round: int = 0
    stage: str = 'queued'
    status: str = 'running'       # running | pr_open | approved | stopped | needs_human
    branch: str = ''
    pr: int = 0
    attempts: int = 0
    design_escalations: int = 0
    tokens: dict = field(default_factory=dict)
    runs: list = field(default_factory=list)   # [{round, run_url, result}]
    stages: dict = field(default_factory=dict)  # stage -> {status, summary, seconds}
    note: str = ''
    comment_id: int = 0


def load(issue: int) -> RunState:
    for c in gh.list_comments(issue):
        m = STATE_RE.search(c.get('body') or '')
        if m and c.get('user', {}).get('type') == 'Bot':
            data = json.loads(m.group(1))
            data['comment_id'] = c['id']
            known = {k: v for k, v in data.items() if k in RunState.__dataclass_fields__}
            return RunState(**known)
    return RunState(issue=issue)


def render(st: RunState) -> str:
    rows = '\n'.join(
        f"| {name} | {info.get('status', '')} | {info.get('summary', '')[:160]} |"
        for name, info in st.stages.items()
    )
    runs = '\n'.join(f"- round {r['round']}: [{r.get('result', '')}]({r['run_url']})" for r in st.runs)
    total = sum(st.tokens.values())
    pr = f'#{st.pr}' if st.pr else '(none yet)'
    payload = json.dumps({k: v for k, v in asdict(st).items() if k != 'comment_id'})
    return (
        f'### AutoSE status: `{st.status}` (stage: {st.stage}, review round {st.round})\n\n'
        f'Pull request: {pr} · Branch: `{st.branch or "-"}` · Tokens so far: {total:,}\n\n'
        f'| Stage | Result | Check |\n|---|---|---|\n{rows}\n\n'
        f'Runs (artifacts are attached to each run):\n{runs}\n\n'
        f'{("**Note:** " + st.note) if st.note else ""}\n\n'
        f'_The workflow never merges. A person decides to merge or close._\n'
        f'<!-- {MARK} {payload} -->'
    )


def save(st: RunState) -> RunState:
    body = render(st)
    if st.comment_id:
        gh.update_comment(st.comment_id, body)
    else:
        st.comment_id = gh.create_comment(st.issue, body)['id']
    return st
