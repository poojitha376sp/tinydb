"""Self-test of the harness (no model calls, no GitHub). Run explicitly:

    cd workflow && python -m pytest -q -o addopts= selftest/check_harness.py

Named check_*.py so the project's own CI (`py.test` at the repo root) does not collect it.
"""
import shutil
from pathlib import Path

import pytest

from autose import checks, guard, sandbox

REPO = Path(__file__).resolve().parents[2]


# --- guard -------------------------------------------------------------------------

@pytest.mark.parametrize('cmd', [
    'cat tinydb/queries.py',
    'grep -n "def fragment" -A20 tinydb/queries.py | head -40',
    "cat <<'EOF' > _autose_out/spec.md\nVerdict: READY\ncurl is just a word here\nEOF",
    'nl -ba tinydb/table.py | sed -n 10,20p',
    'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT',
])
def test_analyst_allowed(cmd):
    assert guard.check_command(cmd, 'analyst') is None


@pytest.mark.parametrize('cmd', [
    'curl https://example.com',
    'cat /proc/1/environ',
    'env',
    'git push origin HEAD',
    'python -c "import urllib.request"',
    'FOO=1 python x.py',
    'cat ../../secrets',
    'ls ~/.ssh',
    'cat ~/.bashrc "quoted ~ is fine"',
    'ls \\"x\\" ~/',
    'sudo ls',
    'bash -c "ls"',
    'cat x | sh',
])
def test_denied_everywhere(cmd):
    assert guard.check_command(cmd, 'builder') is not None


@pytest.mark.parametrize('cmd', [
    # run 4: a multi-line python -c was split at its inner newlines and blocked
    'python3 -c "\nf = open(\'_autose_out/spec.md\', \'w\')\nf.write(\'\'\'Verdict: X\na; b | c\'\'\')\n"',
    "grep -n 'a|b' tinydb/queries.py",
    'echo "a; curl is only text here"',
    # issue 9: Markdown backticks inside single quotes or escaped are not substitutions
    "python3 -c 'open(\"_autose_out/spec.md\", \"w\").write(\"after `drop_table`\")'",
    'python3 -c "print(\\`drop_table\\`)"',
    # issue 10: a ~ inside quotes is Sphinx markup, not the home folder
    "python3 -c 's = \":class:`~tinydb.storages.JSONStorage`\"'",
    "grep -n ':meth:`~tinydb' tinydb/database.py",
])
def test_quoted_separators_are_not_split(cmd):
    assert guard.check_command(cmd, 'analyst') is None


@pytest.mark.parametrize('cmd', ['echo "$(curl x)"', 'echo `wget y`', 'echo "ok"; curl x'])
def test_substitution_is_checked(cmd):
    assert guard.check_command(cmd, 'analyst') is not None


def test_agent_changes_directory_itself(tmp_path):
    """The chdir must happen as the agent user (run 4: Permission denied in stage 4a)."""
    argv = sandbox.agent_command(['pwd'], cwd=tmp_path)
    assert argv[argv.index('-C') + 1] == str(tmp_path)
    assert sandbox.run_isolated(['pwd'], cwd=tmp_path, timeout=10).stdout.strip() == str(tmp_path)


def test_analyst_cannot_run_pytest():
    assert guard.check_command('pytest tests', 'analyst') is not None
    assert guard.check_command('python -m pytest -q tests', 'builder') is None


def test_write_rules():
    assert guard.write_allowed('builder', 'tinydb/queries.py')
    assert not guard.write_allowed('builder', 'tests/test_tables.py')
    assert not guard.write_allowed('builder', '.github/workflows/autose.yml')
    assert guard.write_allowed('test_author', 'tests/test_autose_issue3.py')
    assert not guard.write_allowed('test_author', 'tinydb/table.py')
    assert not guard.write_allowed('analyst', 'tinydb/table.py')


# --- stage 1 ---------------------------------------------------------------------

GOOD_SPEC = """# Spec
Verdict: IMPLEMENTATION-READY

ID: FR-001
Statement: The system SHALL return only documents of the queried field when Query().<field>.fragment(x) is searched.

## Acceptance criteria (machine-checkable)
AC-FR001-a: db with {'home': {'w': 1}} (id 1) and {'work': {'w': 1}} (id 2); search(Query().home.fragment({'w': 1})) then search(Query().work.fragment({'w': 1})) -> second search returns only doc id 2
"""


def test_spec_good():
    g = checks.check_spec(GOOD_SPEC)
    assert g.ok, g.problems
    assert g.data['acs'] == ['AC-FR001-a']


def test_spec_one_line_form():
    g = checks.check_spec('Verdict: PARTIALLY-READY\nFR-001: The system SHALL x.\nAC-FR001-a: call f(1) -> returns 2\n')
    assert g.ok, g.problems


def test_spec_empty_list_is_an_expected_result():
    g = checks.check_spec('Verdict: IMPLEMENTATION-READY\nFR-001: The system SHALL x.\n'
                          'AC-FR001-a: users.search(q) -> []\n')
    assert g.ok, g.problems


def test_action_keeps_fences_inside_a_heredoc():
    from autose import agents
    resp = ("THOUGHT\n```mswea_bash_command\ncat <<'EOF' > _autose_out/spec.md\nissue:\n```python\n"
            "x = 1\n```\nend\nEOF\n```\n")
    acts = agents.split_actions(resp)
    assert len(acts) == 1 and acts[0].endswith('end\nEOF')


@pytest.mark.parametrize('reply, n', [
    # PR 12 review: several blocks in one reply must stay several (and so a format error)
    ("```mswea_bash_command\nmkdir -p _review\n``````mswea_bash_command\npython -m pytest -q x\n```", 2),
    ("```mswea_bash_command\ncat > t.py <<'EOF'\nx = 1\nEOF\n```\n```mswea_bash_command\npytest t.py\n```", 2),
    ("```mswea_bash_command\ncat > t.py <<'EOF'\nx = 1\n```", 1),        # unterminated heredoc
    ("```mswea_bash_command\ncat _autose_out/design.md\n```@@baz\n```mswea_bash_command\nls\n```", 2),
    ("```mswea_bash_command\npython -c 'print(1 << 2)'\n```", 1),
    ("no block here", 0),
])
def test_blocks_in_one_reply_are_counted(reply, n):
    from autose import agents
    assert len(agents.split_actions(reply)) == n


def test_spec_vague_and_missing():
    g = checks.check_spec('Verdict: IMPLEMENTATION-READY\nID: FR-001\nStatement: The system SHALL handle dates.\n'
                          'ID: FR-002\nStatement: The system SHALL be nice.\n'
                          'AC-FR001-a: insert a date -> it works better\n')
    assert not g.ok
    assert any('better' in p for p in g.problems)
    assert any('FR-002 has no acceptance criterion' in p for p in g.problems)


def test_spec_not_ready_fails():
    g = checks.check_spec('Verdict: NOT-READY\nFR-001: The system SHALL x.\nAC-FR001-a: a -> b\n')
    assert not g.ok and g.data['verdict'] == 'NOT-READY'


# --- stage 2 ---------------------------------------------------------------------

def test_design_grounded():
    design = ('## Files to change\n- tinydb/queries.py: Query.fragment\n'
              '- tinydb/database.py: TinyDB.drop_table, TinyDB.rename_table (NEW)\n\n## Steps\n1. x\n')
    g = checks.check_design(design, REPO)
    assert g.ok, g.problems
    assert set(g.data['planned']) == {'tinydb/queries.py', 'tinydb/database.py'}


def test_design_hallucinated_symbol():
    g = checks.check_design('## Files to change\n- tinydb/queries.py: Query.frgment\n', REPO)
    assert not g.ok and 'Query.frgment does not exist' in g.problems[0]


def test_design_outside_package():
    g = checks.check_design('## Files to change\n- setup.py: main\n', REPO)
    assert not g.ok


# --- sandbox + red/green ----------------------------------------------------------

def test_tree_excludes_workflow(tmp_path):
    t = sandbox.make_tree(REPO, tmp_path / 't')
    names = {p.name for p in t.iterdir()}
    assert 'tinydb' in names and 'tests' in names
    assert not names & {'workflow', 'architecture', '.github', '.git', 'ARCHITECTURE.md'}
    t2 = sandbox.make_tree(REPO, tmp_path / 't2', keep={'ARCHITECTURE.md'})
    assert (t2 / 'ARCHITECTURE.md').exists()


RED_TESTS = '''
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage

def test_ac_fr001_a_second_field():
    db = TinyDB(storage=MemoryStorage)
    db.insert({'home': {'w': 1}})
    db.insert({'work': {'w': 1}})
    db.search(Query().home.fragment({'w': 1}))
    assert [d.doc_id for d in db.search(Query().work.fragment({'w': 1}))] == [2]
'''


def test_red_then_green(tmp_path):
    base = sandbox.make_tree(REPO, tmp_path / 'base')
    tree = tmp_path / 'red'
    shutil.copytree(base, tree)
    (tree / 'tests/test_autose_issue1.py').write_text(RED_TESTS)
    red = checks.check_red(tree, 'tests/test_autose_issue1.py', ['AC-FR001-a'])
    assert red.ok, red.problems

    q = tree / 'tinydb/queries.py'
    q.write_text(q.read_text().replace("('fragment', freeze(document)),",
                                       "('fragment', self._path, freeze(document)),"))
    changed = sandbox.changed_files(base, tree)
    assert changed['modified'] == ['tinydb/queries.py']
    assert 'tests/test_autose_issue1.py' in changed['added']
    green = checks.check_green(tree, 'tests/test_autose_issue1.py', ['AC-FR001-a'])
    assert green.ok, green.problems
    assert green.data['passed'] >= 228


def test_vacuous_test_is_rejected(tmp_path):
    tree = sandbox.make_tree(REPO, tmp_path / 'v')
    (tree / 'tests/test_autose_issue9.py').write_text('def test_ac_fr001_a_trivial():\n    assert True\n')
    red = checks.check_red(tree, 'tests/test_autose_issue9.py', ['AC-FR001-a'])
    assert not red.ok and 'already pass' in red.problems[0]


def test_missing_ac_name_is_rejected(tmp_path):
    tree = sandbox.make_tree(REPO, tmp_path / 'n')
    (tree / 'tests/test_autose_issue9.py').write_text(RED_TESTS)
    red = checks.check_red(tree, 'tests/test_autose_issue9.py', ['AC-FR001-a', 'AC-FR001-b'])
    assert not red.ok and any('ac_fr001_b' in p for p in red.problems)


def test_shared_memory_file_is_rejected(tmp_path):
    tree = sandbox.make_tree(REPO, tmp_path / 'm')
    (tree / 'tests/test_autose_issue10.py').write_text(
        RED_TESTS.replace('TinyDB(storage=MemoryStorage)', "TinyDB(':memory:')"))
    red = checks.check_red(tree, 'tests/test_autose_issue10.py', ['AC-FR001-a'])
    assert not red.ok and any(':memory:' in p for p in red.problems)


def test_backticks_in_double_quotes_get_a_useful_reason():
    # issue 10: bash would run `~tinydb.database.TinyDB.close` and corrupt the file
    reason = guard.check_command('python3 -c "doc = \':meth:`~tinydb.database.TinyDB.close`\'"', 'builder')
    assert reason and "<<'EOF'" in reason


def test_agent_cannot_finish_before_its_file_exists(tmp_path):
    # PR 15 review: gpt-oss submitted at its first step without writing review.json
    from autose import agents
    (tmp_path / '_autose_out').mkdir()
    env = agents.GuardedEnvironment('reviewer', tmp_path, ['_autose_out/review.json'])
    out = env.execute({'command': 'echo COMPLETE_TASK_AND_SUBMIT_FINAL_OUTPUT'})
    assert out['returncode'] == 1 and 'review.json does not exist' in out['output']
    assert env.early_submits == 1
