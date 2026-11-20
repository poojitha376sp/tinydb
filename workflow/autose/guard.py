"""Command allowlists and write-path rules per agent role (ADR-005, ADR-009).

Two layers:
1. Before a command runs, ``check_command`` rejects anything outside the
   role's allowlist or containing a denied token (network, sudo, /proc ...).
2. After an agent finishes, the orchestrator diffs the sandbox against the
   base tree and reverts every change outside ``WRITE_RULES`` (the real
   guarantee; layer 1 only stops obvious misuse early).
"""
import re
import shlex

READ_ONLY = {
    'cat', 'head', 'tail', 'ls', 'find', 'grep', 'egrep', 'wc', 'sed', 'nl',
    'sort', 'uniq', 'diff', 'echo', 'printf', 'pwd', 'cd', 'true', 'test',
    'tree', 'cut', 'awk', 'mkdir',
}
CODE_TOOLS = {'python', 'python3', 'pytest', 'pycodestyle', 'mypy', 'touch', 'cp', 'mv', 'rm'}

ALLOW = {
    'analyst': READ_ONLY | {'python', 'python3'},
    'test_author': READ_ONLY | CODE_TOOLS,
    'builder': READ_ONLY | CODE_TOOLS,
    'reviewer': READ_ONLY | CODE_TOOLS,
}

# Paths each role may change inside its sandbox (regex on the relative path).
WRITE_RULES = {
    'analyst': [r'^_autose_out/'],
    'test_author': [r'^tests/test_autose_[A-Za-z0-9_]+\.py$', r'^_autose_out/'],
    'builder': [r'^tinydb/[^/]+\.py$', r'^_autose_out/'],
    'reviewer': [r'.*'],   # throwaway checkout; nothing is ever pushed from it
}

DENY_WORDS = {
    'sudo', 'su', 'curl', 'wget', 'ssh', 'scp', 'nc', 'ncat', 'telnet', 'git',
    'gh', 'pip', 'pip3', 'uv', 'apt', 'apt-get', 'env', 'printenv', 'export',
    'chmod', 'chown', 'kill', 'pkill', 'docker', 'crontab', 'eval', 'exec',
    'source', 'bash', 'sh', 'zsh', 'nohup',
}
DENY_PATTERNS = [
    r'/proc', r'/etc/', r'\.github', r'\.\./', r'(^|\s)~', r'/home/', r'/root',
    r'\burllib\b', r'\bsocket\b', r'\brequests\b', r'\bhttp\.client\b',
    r'\bsubprocess\b', r'\bos\.system\b', r'\bos\.environ\b', r'\bgetenv\b',
]

_HEREDOC = re.compile(r"<<-?\s*(['\"]?)(\w+)\1")


def strip_heredocs(cmd: str) -> str:
    """Remove heredoc bodies so file contents are not parsed as commands."""
    lines, out, end = cmd.split('\n'), [], None
    for line in lines:
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = _HEREDOC.search(line)
        if m:
            end = m.group(2)
    return '\n'.join(out)


def _segments(cmd: str):
    """Split a command line on && || ; | and newlines that are outside quotes.

    Run 4: a multi-line ``python3 -c "..."`` was split at its inner newlines and every
    Python line was then checked as if it were a program name.
    """
    segs, cur, quote, i = [], [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if quote:
            if c == '\\' and quote == '"' and i + 1 < len(cmd):
                cur.append(cmd[i:i + 2])
                i += 2
                continue
            if c == quote:
                quote = None
            cur.append(c)
        elif c in '\'"':
            quote = c
            cur.append(c)
        elif c == '\\' and i + 1 < len(cmd):
            cur.append(cmd[i:i + 2])
            i += 2
            continue
        elif cmd.startswith('&&', i) or cmd.startswith('||', i):
            segs.append(''.join(cur))
            cur = []
            i += 2
            continue
        elif c in ';|\n':
            segs.append(''.join(cur))
            cur = []
        else:
            cur.append(c)
        i += 1
    segs.append(''.join(cur))
    return [s.strip() for s in segs if s.strip()]


def check_command(cmd: str, role: str):
    """Return None if allowed, else a short reason string shown to the agent."""
    visible = strip_heredocs(cmd)
    for pat in DENY_PATTERNS:
        if re.search(pat, visible):
            return f'blocked: pattern {pat!r} is not allowed for any agent'
    # $(...) and `...` run even inside double quotes: check what they would run
    for inner in re.findall(r'\$\(([^()]*)\)', visible) + re.findall(r'`([^`]*)`', visible):
        reason = check_command(inner, role) if inner.strip() else None
        if reason:
            return reason
    for seg in _segments(visible):
        seg = seg.lstrip('({ ').rstrip(')} ')
        if not seg:
            continue
        try:
            words = shlex.split(seg, posix=True)
        except ValueError:
            words = seg.split()
        if not words:
            continue
        for w in words:
            if w in DENY_WORDS:
                return f'blocked: {w!r} is not allowed for any agent'
        first = words[0]
        if re.match(r'^\w+=', first):
            return 'blocked: setting environment variables is not allowed'
        if first.startswith('$(') or first.startswith('`'):
            return 'blocked: command substitution as a command is not allowed'
        name = first.rsplit('/', 1)[-1]
        if name not in ALLOW[role]:
            allowed = ', '.join(sorted(ALLOW[role]))
            return f'blocked: {name!r} is not in the {role} allowlist ({allowed})'
    return None


def write_allowed(role: str, rel_path: str) -> bool:
    return any(re.search(rule, rel_path) for rule in WRITE_RULES[role])
