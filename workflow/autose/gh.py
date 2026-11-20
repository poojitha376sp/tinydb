"""The only code that talks to GitHub (ADR-005). Uses the `gh` CLI with the
job's GITHUB_TOKEN taken from the environment (GH_TOKEN), never passed on
the command line. Agents never import or call this module.
"""
import json
import os
import subprocess
import time

REPO = os.environ.get('GITHUB_REPOSITORY', '')


def gh(*args, input_text=None, check=True) -> str:
    proc = subprocess.run(['gh', *args], input=input_text, capture_output=True, text=True)
    if check and proc.returncode != 0:
        raise RuntimeError(f'gh {" ".join(args[:3])} failed: {proc.stderr.strip()[:500]}')
    return proc.stdout


def api(path, method='GET', fields=None, check=True):
    args = ['api', '-X', method, path, '-H', 'Accept: application/vnd.github+json']
    body = None
    if fields is not None:
        args += ['--input', '-']
        body = json.dumps(fields)
    out = gh(*args, input_text=body, check=check)
    return json.loads(out) if out.strip() else {}


def get_issue(number: int) -> dict:
    return api(f'repos/{REPO}/issues/{number}')


def list_comments(number: int) -> list:
    return json.loads(gh('api', '--paginate', f'repos/{REPO}/issues/{number}/comments'))


def create_comment(number: int, body: str) -> dict:
    return api(f'repos/{REPO}/issues/{number}/comments', 'POST', {'body': body})


def update_comment(comment_id: int, body: str) -> dict:
    return api(f'repos/{REPO}/issues/comments/{comment_id}', 'PATCH', {'body': body})


def add_labels(number: int, labels) -> None:
    api(f'repos/{REPO}/issues/{number}/labels', 'POST', {'labels': list(labels)})


def remove_label(number: int, label: str) -> None:
    api(f'repos/{REPO}/issues/{number}/labels/{label}', 'DELETE', check=False)


def find_pr_for_branch(branch: str):
    owner = REPO.split('/')[0]
    prs = api(f'repos/{REPO}/pulls?state=open&head={owner}:{branch}')
    return prs[0] if prs else None


def create_pr(branch: str, base: str, title: str, body: str) -> dict:
    return api(f'repos/{REPO}/pulls', 'POST',
               {'title': title, 'head': branch, 'base': base, 'body': body})


def update_pr(number: int, body: str) -> dict:
    return api(f'repos/{REPO}/pulls/{number}', 'PATCH', {'body': body})


def pr_files_diff(number: int) -> str:
    return gh('pr', 'diff', str(number), '--repo', REPO)


def dispatch(workflow_file: str, ref: str, inputs: dict) -> None:
    api(f'repos/{REPO}/actions/workflows/{workflow_file}/dispatches', 'POST',
        {'ref': ref, 'inputs': {k: str(v) for k, v in inputs.items()}})


def wait_for_ci(workflow_file: str, branch: str, sha: str, timeout: int, poll=20) -> dict:
    """Wait for the dispatched CI run on ``sha``; return {'conclusion', 'url'}."""
    deadline = time.time() + timeout
    run = None
    while time.time() < deadline:
        runs = api(f'repos/{REPO}/actions/workflows/{workflow_file}/runs'
                   f'?branch={branch}&event=workflow_dispatch&per_page=20').get('workflow_runs', [])
        matching = [r for r in runs if r.get('head_sha') == sha]
        if matching:
            run = matching[0]
            if run.get('status') == 'completed':
                return {'conclusion': run.get('conclusion'), 'url': run.get('html_url')}
        time.sleep(poll)
    return {'conclusion': 'timed_out', 'url': run.get('html_url') if run else None}


def run_url() -> str:
    server = os.environ.get('GITHUB_SERVER_URL', 'https://github.com')
    return f"{server}/{REPO}/actions/runs/{os.environ.get('GITHUB_RUN_ID', '')}"
