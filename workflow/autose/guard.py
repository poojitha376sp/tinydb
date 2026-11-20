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

# Bash expands ~ only outside quotes, so this pattern is checked on the unquoted text only.
# (Issue 10: "~tinydb.storages" inside a python3 -c "..." docstring edit was blocked, and the
# Builder then removed the ~ from four docstrings to get past the guard.)
UNQUOTED_ONLY = {r'(^|\s)~'}


def _unquoted(cmd: str) -> str:
    """The command with everything inside '...' or "..." replaced by spaces."""
    out, quote, i = [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if quote:
            if c == '\\' and quote == '"' and i + 1 < len(cmd):
                out.append('  ')
                i += 2
                continue
            if c == quote:
                quote = None
                out.append(c)
            else:
                out.append('\n' if c == '\n' else ' ')
        elif c == '\\' and i + 1 < len(cmd):
            out.append(cmd[i:i + 2])                 # escaped quote outside quotes stays literal
            i += 2
            continue
        elif c in '\'"':
            quote = c
            out.append(c)
        else:
            out.append(c)
        i += 1
    return ''.join(out)


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


def _substitutions(cmd: str):
    """Bodies of $(...) and `...` that bash would really run: not inside single quotes and
    not escaped. (Issue 9: Markdown backticks inside python3 -c '...' were wrongly blocked.)"""
    out, quote, i = [], None, 0
    while i < len(cmd):
        c = cmd[i]
        if quote == "'":
            if c == "'":
                quote = None
        elif c == '\\':
            i += 1                                   # escaped character, never a substitution
        elif c == "'" and quote is None:
            quote = "'"
        elif c == '"':
            quote = None if quote == '"' else '"'
        elif c == '`':
            j = i + 1
            while j < len(cmd) and cmd[j] != '`':
                j += 2 if cmd[j] == '\\' else 1
            out.append(cmd[i + 1:j])
            i = j
        elif cmd.startswith('$(', i):
            depth, j = 1, i + 2
            while j < len(cmd) and depth:
                depth += {'(': 1, ')': -1}.get(cmd[j], 0)
                j += 1
            out.append(cmd[i + 2:j - 1])
            i = j - 1
        i += 1
    return out


def check_command(cmd: str, role: str):
    """Return None if allowed, else a short reason string shown to the agent."""
    visible = strip_heredocs(cmd)
    bare = _unquoted(visible)
    for pat in DENY_PATTERNS:
        if re.search(pat, bare if pat in UNQUOTED_ONLY else visible):
            return f'blocked: pattern {pat!r} is not allowed for any agent'
    # $(...) and `...` run even inside double quotes: check what they would run
    for inner in _substitutions(visible):
        reason = check_command(inner, role) if inner.strip() else None
        if reason:
            # Issue 10: Sphinx markup like :meth:`~tinydb.x` inside python3 -c "..." is run by
            # bash as a command, so say how to write such text instead of only what was blocked.
            return (f'{reason}. Note: bash runs `...` and $(...) even inside double quotes, so '
                    f'`{inner.strip()[:40]}` would be run as a command. To write code or text that '
                    "contains backticks, use a heredoc with a quoted delimiter: cat > FILE <<'EOF'")
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
