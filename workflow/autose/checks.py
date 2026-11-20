"""Stage gates (ADR-007). Deterministic and grounding checks only; the plain
code here decides pass or fail, never an LLM.

Every function returns a ``Gate``: ok flag, a list of human-readable
problems (fed back to the agent on a retry and written to the artifact),
and any data later stages need.
"""
import ast
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

from . import sandbox

# Vague words from the A1 requirements-spec-builder skill, plus a few common ones.
VAGUE_WORDS = [
    'sovereign', 'enterprise-grade', 'fast', 'secure', 'autonomous', 'scalable',
    'user-friendly', 'better', 'easy', 'easily', 'nice', 'appropriate',
    'appropriately', 'properly', 'robust', 'intuitive', 'etc', 'and so on',
    'reasonable', 'as needed', 'efficient',
]

# The A1 skill writes item records ("ID: FR-001" then "Statement: The system SHALL ...");
# a one-line form "FR-001: The system SHALL ..." is accepted too.
FR_RE = re.compile(r'^\s*[-*]?\s*(?:ID:\s*)?\**(FR-\d{3})\**\s*:?\s*(.*)$')
STATEMENT_RE = re.compile(r'^\s*[-*]?\s*\**Statement:?\**\s*(.+)$')
AC_RE = re.compile(r'^\s*[-*]?\s*\**(AC-FR\d{3}-[a-z])\**:\s*(.+?)\s*->\s*(.+)$')
VERDICT_RE = re.compile(
    r'^\s*[-*]?\s*\**Verdict:?\**\s*\**(IMPLEMENTATION-READY|PARTIALLY-READY|NOT-READY|READY)\b', re.M)


@dataclass
class Gate:
    ok: bool
    problems: list = field(default_factory=list)
    data: dict = field(default_factory=dict)

    def summary(self) -> str:
        if self.ok:
            return 'PASS'
        return 'FAIL: ' + '; '.join(self.problems)


def ac_test_token(ac_id: str) -> str:
    """AC-FR001-a -> ac_fr001_a (must appear in the test function name)."""
    return ac_id.lower().replace('-', '_')


# --- Stage 1 -----------------------------------------------------------------

def check_spec(text: str) -> Gate:
    problems = []
    m = VERDICT_RE.search(text)
    verdict = m.group(1) if m else None
    if not verdict:
        problems.append('missing "Verdict: READY|PARTIALLY-READY|NOT-READY" line')
    elif verdict == 'NOT-READY':
        problems.append('the spec says NOT-READY: the issue cannot be specified without answers '
                        'from a person (see open questions)')

    frs, acs, current = {}, {}, None
    for line in text.splitlines():
        am = AC_RE.match(line)
        if am:
            acs[am.group(1)] = (am.group(2), am.group(3))
            continue
        fm = FR_RE.match(line)
        if fm:
            current = fm.group(1)
            frs[current] = frs.get(current, '') + ' ' + fm.group(2)
            continue
        sm = STATEMENT_RE.match(line)
        if sm and current:
            frs[current] += ' ' + sm.group(1)

    if not frs:
        problems.append('no requirement lines of the form "FR-001: The system SHALL ..."')
    for fr, stmt in frs.items():
        if 'SHALL' not in stmt:
            problems.append(f'{fr} does not use SHALL')
    if not acs:
        problems.append('no acceptance criteria of the form "AC-FR001-a: <input/action> -> <expected result>"')
    for ac, (given, expected) in acs.items():
        fr = 'FR-' + ac[5:8]
        if fr not in frs:
            problems.append(f'{ac} refers to {fr}, which does not exist')
        words = re.findall(r"[a-z][a-z-]*", f'{given} {expected}'.lower())
        joined = ' '.join(words)
        for vague in VAGUE_WORDS:
            if re.search(rf'\b{re.escape(vague)}\b', joined):
                problems.append(f'{ac} uses the untestable word "{vague}"')
        if not expected.strip():   # "[]", "0" and "None" are fine (issue 9 was stopped on "-> []")
            problems.append(f'{ac} has no observable expected result after "->"')
    for fr in frs:
        if not any(ac[3:8] == fr.replace('-', '') for ac in acs):
            problems.append(f'{fr} has no acceptance criterion')

    return Gate(not problems, problems, {'verdict': verdict, 'frs': frs, 'acs': sorted(acs)})


# --- Stage 2 -----------------------------------------------------------------

ENTRY_RE = re.compile(r'^\s*[-*]\s+`?(?P<path>[\w./-]+\.py)`?\s*(?P<new>\(NEW\))?\s*(?::\s*(?P<syms>.*))?$')


def _defined_symbols(py: Path) -> set:
    tree = ast.parse(py.read_text())
    names = set()
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            names.add(node.name)
        if isinstance(node, ast.ClassDef):
            for sub in node.body:
                if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    names.add(f'{node.name}.{sub.name}')
        if isinstance(node, ast.Assign):
            for t in node.targets:
                if isinstance(t, ast.Name):
                    names.add(t.id)
    return names


def check_design(text: str, base: Path) -> Gate:
    problems, planned = [], {}
    section = re.search(r'^##\s*Files to change\s*$(.*?)(?=^##\s|\Z)', text, re.M | re.S)
    if not section:
        return Gate(False, ['missing "## Files to change" section'])
    for line in section.group(1).splitlines():
        if not line.strip():
            continue
        m = ENTRY_RE.match(line)
        if not m:
            continue
        rel, new_file = m.group('path'), bool(m.group('new'))
        if rel.startswith('tests/'):
            continue  # tests are written by the Test Author, not planned here
        if not rel.startswith('tinydb/'):
            problems.append(f'{rel}: only files inside tinydb/ may be changed')
            continue
        path = base / rel
        if not path.exists() and not new_file:
            problems.append(f'{rel} does not exist (mark it "(NEW)" if it is a new file)')
            continue
        syms = [s.strip() for s in (m.group('syms') or '').split(',') if s.strip()]
        if not syms:
            problems.append(f'{rel}: name at least one function or class to change')
        known = _defined_symbols(path) if path.exists() else set()
        for sym in syms:
            is_new = '(NEW)' in sym
            name = sym.replace('(NEW)', '').strip().strip('`').rstrip('()')
            if not is_new and not new_file and name not in known:
                problems.append(f'{rel}: {name} does not exist (mark it "(NEW)" if it is new)')
        planned[rel] = syms
    if not planned and not problems:
        problems.append('no files listed under "## Files to change"')
    return Gate(not problems, problems, {'planned': planned})


# --- Running tests in a sandbox ----------------------------------------------

def run_pytest(tree: Path, targets, timeout=600) -> dict:
    """Run pytest as the agent user; return per-test outcomes from JUnit XML."""
    out = tree / '_autose_out'
    out.mkdir(exist_ok=True)
    junit = out / 'junit.xml'
    if junit.exists():
        junit.unlink()
    sandbox.give_to_agent(tree)
    try:
        proc = sandbox.run_isolated(
            ['python', '-m', 'pytest', '-q', '-o', 'addopts=', '-p', 'no:cacheprovider',
             '--tb=no', '-rN', f'--junitxml={junit}', *targets],
            cwd=tree, timeout=timeout)
    finally:
        sandbox.take_back(tree)
    results = {}
    if junit.exists():
        for case in ET.parse(junit).getroot().iter('testcase'):
            tid = f"{case.get('classname', '')}::{case.get('name', '')}"
            outcome, msg = 'passed', ''
            for tag in ('failure', 'error', 'skipped'):
                el = case.find(tag)
                if el is not None:
                    outcome = 'skipped' if tag == 'skipped' else 'failed'
                    msg = (el.get('message') or '').strip()[:400]
            results[tid] = {'outcome': outcome, 'message': msg}
    return {'returncode': proc.returncode, 'tests': results,
            'tail': (proc.stdout + proc.stderr)[-1500:]}


def _tests_for(results: dict, test_file: str) -> dict:
    stem = Path(test_file).stem
    return {t: r for t, r in results['tests'].items() if stem in t}


# --- Stage 4a: tests must be red on the base code ------------------------------

def check_red(base_with_tests: Path, test_file: str, acs) -> Gate:
    problems = []
    src = (base_with_tests / test_file)
    if not src.exists():
        return Gate(False, [f'{test_file} was not written'])
    try:
        tree = ast.parse(src.read_text())
    except SyntaxError as e:
        return Gate(False, [f'{test_file} has a syntax error: {e}'])
    names = [n.name for n in ast.walk(tree)
             if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name.startswith('test')]
    if not names:
        problems.append('no test functions found')
    for ac in acs:
        if not any(ac_test_token(ac) in n for n in names):
            problems.append(f'no test function name contains "{ac_test_token(ac)}" for {ac}')
    if re.search(r'''TinyDB\(\s*['"]:memory:['"]''', src.read_text()):
        # Issue 10: TinyDB(':memory:') is a real JSON file named ":memory:" that every test
        # shares, so one test's leftover table made a correct fix fail three times.
        problems.append("TinyDB(':memory:') writes a real file named :memory: that all tests share; "
                        'use TinyDB(storage=MemoryStorage) or a file under tmp_path')

    res = run_pytest(base_with_tests, [test_file])
    mine = _tests_for(res, test_file)
    collection_error = not mine or all('::' not in t or t.endswith('::') for t in mine)
    if not mine:
        # The module could not be imported against the base code (e.g. a new
        # function does not exist yet): every test is red by construction.
        tail = res['tail']
        if not re.search(r'ImportError|AttributeError|NameError|ModuleNotFoundError', tail):
            problems.append(f'tests could not be collected for an unexpected reason: {tail[-300:]}')
    else:
        green = [t for t, r in mine.items() if r['outcome'] == 'passed']
        if green:
            problems.append('these tests already pass on the unchanged code, so they do not test the '
                            'change: ' + ', '.join(t.split('::')[-1] for t in green))
    return Gate(not problems, problems, {'tests': names, 'red': mine, 'collection_error': collection_error})


# --- Stage 3: build -------------------------------------------------------------

def check_build(tree: Path, changed: dict, planned: dict) -> Gate:
    problems = []
    sandbox.give_to_agent(tree)
    try:
        for argv, label in (
            (['python', '-m', 'compileall', '-q', 'tinydb'], 'compile'),
            (['python', '-c', 'import tinydb'], 'import tinydb'),
            (['python', '-m', 'mypy', 'tinydb'], 'mypy (as in the project CI)'),
        ):
            p = sandbox.run_isolated(argv, cwd=tree, timeout=300)
            if p.returncode != 0:
                problems.append(f'{label} failed: {(p.stdout + p.stderr)[-600:]}')
    finally:
        sandbox.take_back(tree)
    touched = changed['added'] + changed['modified'] + changed['deleted']
    if not touched:
        problems.append('no files were changed')
    outside = [p for p in touched if p.startswith('tinydb/') and p not in planned]
    if outside:
        problems.append('changed files that design.md does not name: ' + ', '.join(outside))
    return Gate(not problems, problems, {'touched': touched})


# --- Stage 4b: green -----------------------------------------------------------

def check_green(eval_tree: Path, test_file: str, acs) -> Gate:
    res = run_pytest(eval_tree, ['tests'])
    failing = {t: r for t, r in res['tests'].items() if r['outcome'] == 'failed'}
    mine = _tests_for(res, test_file)
    problems = []
    if not res['tests']:
        problems.append('the test suite could not run: ' + res['tail'][-400:])
    if not mine:
        problems.append(f'none of the new tests in {test_file} ran')
    if failing:
        problems.append(f'{len(failing)} test(s) fail')
    signature = sorted((t, r['message'].split(':')[0][:80]) for t, r in failing.items())
    passed = sum(1 for r in res['tests'].values() if r['outcome'] == 'passed')
    return Gate(not problems, problems, {
        'failing': failing, 'signature': signature, 'passed': passed,
        'total': len(res['tests']), 'new_tests': mine,
    })
