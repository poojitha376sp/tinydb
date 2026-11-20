"""Stage 6, part 1: the independent Reviewer (ADR-008).

Runs in its own job whose token can only read the repository and call
GitHub Models. It sees the issue, the diff and a checkout of the PR head
(plus ARCHITECTURE.md); never spec.md, design.md, test reports or any
transcript. Its JSON verdict is then checked by plain code:

- a finding must cite a command the Reviewer really ran in this session
  (checked against its trajectory) and a real file/line, else it is dropped;
- APPROVE needs the break-it test to have been run, no must-fix finding and
  an average score >= 7, else the result is INCONCLUSIVE (a person decides).

Usage:
    python -m autose.review --pr 12 --issue 3 --round 0 --variant independent --out review_out/
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

from . import agents, config, gh, guard, sandbox

WORK = Path(os.environ.get('AUTOSE_WORK', '/tmp/autose'))


def executed_commands(trajectory: Path, blocked=()) -> list:
    """Commands the agent really ran: from its trajectory, minus those the guard blocked."""
    data = json.loads(trajectory.read_text()) if trajectory.exists() else {}
    refused = {b['command'] for b in blocked}
    cmds = []
    for m in data.get('messages', []):
        for a in (m.get('extra') or {}).get('actions', []) or []:
            c = a.get('command', '')
            if c[:300] not in refused:
                # Only the command itself counts, not text it writes into a file: otherwise the
                # heredoc that writes review.json would "contain" every claimed evidence command.
                cmds.append(guard.strip_heredocs(c))
    return cmds


def _ran(cmd: str, cmds) -> bool:
    """The cited command must be (part of) a command that was really run, not the other way round."""
    cmd = ' '.join((cmd or '').split())
    return len(cmd) >= 4 and any(cmd in ' '.join(c.split()) for c in cmds)


def judge(raw: dict, cmds, tree: Path, variant: str) -> dict:
    """Turn the Reviewer's JSON into the final, rule-checked verdict."""
    kept, dropped = [], []
    for f in raw.get('findings', []) or []:
        path = tree / str(f.get('file', ''))
        line_ok = path.is_file() and 0 < int(f.get('line') or 0) <= len(path.read_text().splitlines()) + 1
        evidence_ok = _ran(f.get('evidence_command', ''), cmds)
        if variant == 'baseline' or (line_ok and evidence_ok):
            kept.append(f)
        else:
            why = []
            if not line_ok:
                why.append('file/line does not exist')
            if not evidence_ok:
                why.append('evidence command was never run')
            dropped.append({**f, 'dropped_because': ', '.join(why)})
    must_fix = [f for f in kept if f.get('severity') == 'must-fix']
    scores = [v for v in (raw.get('scores') or {}).values() if isinstance(v, (int, float))]
    avg = sum(scores) / len(scores) if scores else 0
    claimed = raw.get('verdict')
    break_it = raw.get('break_it') or {}
    break_ok = _ran(break_it.get('command', ''), cmds) and (tree / '_review').exists()

    if claimed not in ('APPROVE', 'REQUEST_CHANGES'):
        verdict, reason = 'INCONCLUSIVE', 'no valid verdict in review.json'
    elif variant == 'baseline':
        verdict, reason = claimed, 'baseline variant: verdict taken as given'
    elif must_fix:
        verdict, reason = 'REQUEST_CHANGES', f'{len(must_fix)} must-fix finding(s) with evidence'
    elif claimed == 'REQUEST_CHANGES':
        verdict, reason = 'INCONCLUSIVE', 'changes requested but no finding had evidence'
    elif not break_ok:
        verdict, reason = 'INCONCLUSIVE', 'approval without a break-it test that was actually run'
    elif avg < 7:
        verdict, reason = 'INCONCLUSIVE', f'approval with average score {avg:.1f} < 7'
    else:
        verdict, reason = 'APPROVE', 'no must-fix findings, break-it test run, scores >= 7'
    route = 'approach' if any(f.get('route') == 'approach' for f in must_fix) else 'code'
    return {'verdict': verdict, 'reason': reason, 'route': route if verdict == 'REQUEST_CHANGES' else '',
            'claimed_verdict': claimed, 'average_score': round(avg, 2), 'break_it_run': break_ok,
            'kept_findings': kept, 'dropped_findings': dropped, 'summary': raw.get('summary', '')}


def render_md(result: dict, args, models) -> str:
    lines = [f"## AutoSE independent review: **{result['verdict']}**", '',
             f"{result['summary']}", '',
             f"- Rule check: {result['reason']}",
             f"- Reviewer's own verdict: {result['claimed_verdict']}; average score {result['average_score']}",
             f"- Break-it test run: {'yes' if result['break_it_run'] else 'no'}",
             f"- Model(s): {', '.join(models)} · variant: {args.variant} · round {args.round}", '']
    if result['kept_findings']:
        lines += ['### Findings', '']
        for f in result['kept_findings']:
            lines += [f"- **{f.get('severity')}** ({f.get('route')}) `{f.get('file')}:{f.get('line')}`: {f.get('claim')}",
                      f"  - evidence: `{f.get('evidence_command', '')}`",
                      f"  - output: {str(f.get('evidence_output', ''))[:300]}"]
    if result['dropped_findings']:
        lines += ['', '### Dropped (no evidence)', '']
        lines += [f"- {f.get('claim')} ({f['dropped_because']})" for f in result['dropped_findings']]
    lines += ['', '_The reviewer cannot push or merge. A person decides._']
    return '\n'.join(lines) + '\n'


def pr_diff(repo: Path) -> str:
    """The PR's changes against master (runs on the Actions runner only)."""
    return subprocess.run(['git', 'diff', 'origin/master...HEAD'], cwd=repo, capture_output=True,
                          text=True, check=True).stdout


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--pr', type=int, required=True)
    p.add_argument('--issue', type=int, required=True)
    p.add_argument('--round', type=int, default=0)
    p.add_argument('--variant', default='independent', choices=['independent', 'baseline'])
    p.add_argument('--out', default='review_out')
    p.add_argument('--pr-dir', default='.', help='checkout of the PR head')
    args = p.parse_args(argv)

    repo = Path(args.pr_dir).resolve()   # checkout of the PR head; the harness itself runs from master
    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    WORK.mkdir(parents=True, exist_ok=True)
    os.chmod(WORK, 0o755)

    issue = gh.get_issue(args.issue)
    diff = pr_diff(repo)
    (out / 'reviewed.diff').write_text(diff)
    tree = sandbox.make_tree(repo, WORK / 'review', keep={'ARCHITECTURE.md'})
    (tree / '_autose_out').mkdir()

    issue_text = (issue.get('body') or '').replace('</untrusted_issue>', '')
    task = (f'Review pull request #{args.pr} for issue #{args.issue}.\n\n'
            f'<untrusted_issue>\nTitle: {issue.get("title", "")}\n\n{issue_text}\n</untrusted_issue>\n\n'
            f'The diff of the pull request:\n```diff\n{diff[:30000]}\n```\n')
    if args.variant == 'baseline':
        pr = gh.api(f'repos/{gh.REPO}/pulls/{args.pr}')
        task += f'\nPull request description by its author:\n{pr.get("body") or ""}\n'
        models, prompt = [config.BUILD_MODEL], 'reviewer_baseline'
    else:
        models, prompt = config.REVIEW_MODELS, 'reviewer'

    traj = out / 'reviewer_trajectory.json'
    run = agents.run_agent('reviewer', prompt, task, tree, traj, models=models)
    raw_path = tree / '_autose_out/review.json'
    try:
        raw = json.loads(raw_path.read_text())
    except Exception as e:
        raw = {'verdict': None, 'summary': f'review.json missing or invalid: {e}'}
        if run['exit_status'].startswith('Error'):
            raw['summary'] = f"the reviewer could not run ({run['exit_status']}): {run.get('error', '')[:400]}"
    result = judge(raw, executed_commands(traj, run['blocked']), tree, args.variant)
    result.update({'pr': args.pr, 'issue': args.issue, 'round': args.round, 'variant': args.variant,
                   'agent': run, 'tokens': agents.total_tokens(), 'run_url': gh.run_url()})
    (out / 'review_raw.json').write_text(json.dumps(raw, indent=2))
    (out / 'review_result.json').write_text(json.dumps(result, indent=2))
    (out / 'review.md').write_text(render_md(result, args, run['models'] or models))
    print(result['verdict'], result['reason'])


if __name__ == '__main__':
    main()
