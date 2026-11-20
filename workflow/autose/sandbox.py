"""Agent sandboxes: clean copies of the project, file diffs, and running code
as a separate unprivileged user with an empty environment (ADR-005).

On GitHub runners the workflow creates the user ``autose-agent`` and sets
``AUTOSE_SANDBOX_USER``. Commands then run via ``sudo -u autose-agent env -i``
so an agent cannot read the runner's environment (GITHUB_TOKEN) through
/proc, and owns only its own sandbox directory. Locally, without that
variable, commands still run with an empty environment.
"""
import difflib
import filecmp
import os
import shutil
import subprocess
import sys
from pathlib import Path

from . import config

IGNORE_PARTS = {'__pycache__', '.pytest_cache', '.mypy_cache', '_autose_out'}
# The Python that runs the workflow (with pytest, mypy, pycodestyle installed)
# comes first, so agents use the same interpreter and tools.
SAFE_PATH = f'{Path(sys.executable).parent}:/usr/local/bin:/usr/bin:/bin'


def make_tree(src: Path, dst: Path, exclude=None, keep=()) -> Path:
    """Copy the project at ``src`` to ``dst`` without workflow/experiment files.

    ``keep`` names top-level entries to copy even if they are excluded
    (the Reviewer keeps ARCHITECTURE.md, ADR-003).
    """
    exclude = set(config.SANDBOX_EXCLUDE if exclude is None else exclude) - set(keep)
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for entry in sorted(src.iterdir()):
        if entry.name in exclude:
            continue
        target = dst / entry.name
        if entry.is_dir():
            shutil.copytree(entry, target, ignore=shutil.ignore_patterns(*IGNORE_PARTS, '*.pyc'))
        else:
            shutil.copy2(entry, target)
    return dst


def _files(root: Path):
    out = {}
    for p in root.rglob('*'):
        rel = p.relative_to(root)
        if p.is_file() and not (set(rel.parts) & IGNORE_PARTS) and p.suffix != '.pyc':
            out[rel.as_posix()] = p
    return out


def changed_files(base: Path, new: Path) -> dict:
    """Return {'added': [...], 'modified': [...], 'deleted': [...]} relative paths."""
    a, b = _files(base), _files(new)
    return {
        'added': sorted(set(b) - set(a)),
        'deleted': sorted(set(a) - set(b)),
        'modified': sorted(p for p in set(a) & set(b) if not filecmp.cmp(a[p], b[p], shallow=False)),
    }


def unified_diff(base: Path, new: Path, paths) -> str:
    """A git-style unified diff of ``paths`` between two trees."""
    chunks = []
    for rel in sorted(paths):
        old_p, new_p = base / rel, new / rel
        old = old_p.read_text().splitlines(keepends=True) if old_p.exists() else []
        cur = new_p.read_text().splitlines(keepends=True) if new_p.exists() else []
        chunks.append(f'diff --git a/{rel} b/{rel}\n')
        chunks.extend(difflib.unified_diff(
            old, cur,
            fromfile=f'a/{rel}' if old_p.exists() else '/dev/null',
            tofile=f'b/{rel}' if new_p.exists() else '/dev/null',
        ))
    return ''.join(chunks)


def revert(base: Path, new: Path, rel: str) -> None:
    """Put one path in ``new`` back to its state in ``base``."""
    src, dst = base / rel, new / rel
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    elif dst.exists():
        dst.unlink()


def sandbox_user():
    return os.environ.get('AUTOSE_SANDBOX_USER') or None


def give_to_agent(path: Path) -> None:
    """Hand a sandbox directory to the agent user (no-op locally)."""
    user = sandbox_user()
    if user:
        subprocess.run(['sudo', '-n', 'chown', '-R', f'{user}:{user}', str(path)], check=True)


def take_back(path: Path) -> None:
    """Return a sandbox directory to the runner user after the agent finished.

    The directory is then closed to everyone else (mode 700), so a later agent
    (same Unix user) cannot read an earlier agent's work, e.g. the Builder
    cannot open the Test Author's test file (ADR-003).
    """
    if sandbox_user():
        me = f'{os.getuid()}:{os.getgid()}'
        subprocess.run(['sudo', '-n', 'chown', '-R', me, str(path)], check=True)
    os.chmod(path, 0o700)


def agent_command(argv, extra_env=None):
    """Wrap ``argv`` so it runs as the agent user with an empty environment."""
    env = [f'PATH={SAFE_PATH}', 'HOME=/tmp', 'LANG=C.UTF-8', 'PYTHONDONTWRITEBYTECODE=1']
    for k, v in (extra_env or {}).items():
        env.append(f'{k}={v}')
    user = sandbox_user()
    prefix = ['sudo', '-n', '-u', user] if user else []
    return prefix + ['env', '-i', *env, *argv]


def run_isolated(argv, cwd: Path, timeout: int, extra_env=None) -> subprocess.CompletedProcess:
    """Run a command as the agent user, in ``cwd``, with a clean environment."""
    return subprocess.run(
        agent_command(argv, extra_env), cwd=str(cwd), capture_output=True,
        text=True, timeout=timeout,
    )
