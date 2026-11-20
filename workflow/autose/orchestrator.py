"""Stages 1 to 5 as a plain-Python state machine (ADR-002).

    1 Analyst -> spec.md            gate: check_spec
    2 Analyst -> design.md          gate: check_design (grounded in the base code)
    4a Test Author -> tests         gate: check_red (every new test fails on the base code)
    3 Builder -> code change        gate: check_build (compile, import, mypy, scope)
    4b run all tests                gate: check_green; fail -> back to 3 (max 3 attempts),
                                    same failure twice -> back to 2 (once)
    5 Release (plain code)          push branch, open/update PR, dispatch CI, wait for green

Usage (from .github/workflows/autose.yml):
    python -m autose.orchestrator --issue 3 --round 0 --resume-from 1 --out out/
"""
import argparse
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

from . import agents, checks, config, gh, guard, sandbox, state

WORK = Path(os.environ.get('AUTOSE_WORK', '/tmp/autose'))
CI_WORKFLOW = 'ci-workflow.yml'


class Stop(Exception):
    """A stage could not pass its check: explain in the artifact and stop."""

    def __init__(self, stage, reason):
        super().__init__(reason)
        self.stage, self.reason = stage, reason


class Run:
    def __init__(self, args):
        self.args = args
        self.repo = Path(os.environ.get('GITHUB_WORKSPACE', '.')).resolve()
        self.out = Path(args.out).resolve()
        (self.out / 'trajectories').mkdir(parents=True, exist_ok=True)
        WORK.mkdir(parents=True, exist_ok=True)
        os.chmod(WORK, 0o755)
        self.issue_no = args.issue
        self.results = {'issue': args.issue, 'round': args.round, 'resume_from': args.resume_from,
                        'arch_context': args.arch_context, 'stages': {}, 'run_url': gh.run_url()}
        self.st = None
        self.test_file = f'tests/test_autose_issue{args.issue}.py'

    # --- bookkeeping ------------------------------------------------------------

    def record(self, stage, status, summary, **extra):
        info = {'status': status, 'summary': summary, **extra}
        self.results['stages'][stage] = info
        self.st.stage = stage
        self.st.stages[stage] = {'status': status, 'summary': summary}
        self.st.tokens = {r: u.total for r, u in agents.USAGE.items()}
        state.save(self.st)
        self.dump()

    def dump(self):
        self.results['tokens'] = {r: {'prompt': u.prompt, 'completion': u.completion, 'calls': u.calls}
                                  for r, u in agents.USAGE.items()}
        self.results['tokens_total'] = agents.total_tokens()
        (self.out / 'stage_results.json').write_text(json.dumps(self.results, indent=2))

    def write(self, name, text):
        (self.out / name).write_text(text)

    # --- trees ---------------------------------------------------------------

    def fresh_tree(self, name, extra_files=None):
        tree = sandbox.make_tree(self.base, WORK / name)
        outdir = tree / '_autose_out'
        outdir.mkdir()
        for fname, text in (extra_files or {}).items():
            (outdir / fname).write_text(text)
        return tree

    def enforce_writes(self, role, tree, base=None):
        """Revert every change outside the role's write rules (ADR-005)."""
        base = base or self.base
        ch = sandbox.changed_files(base, tree)
        reverted = []
        for rel in ch['added'] + ch['modified'] + ch['deleted']:
            if not guard.write_allowed(role, rel):
                sandbox.revert(base, tree, rel)
                reverted.append(rel)
        return reverted

    def agent_ran(self, stage, run):
        """A model or harness error is not a gate failure: stop at once and say why (ADR-009)."""
        status = run.get('exit_status', '')
        if status.startswith(('Error', 'TokenCapExceeded', 'QuotaExhausted')):
            self.results['stages'][stage] = {'status': 'error', 'summary': status, 'agent': run}
            raise Stop(stage, f"the agent could not run ({status}): {run.get('error', '')[:400]}")

    # --- stages ------------------------------------------------------------------

    def issue_block(self):
        body = (self.issue.get('body') or '').replace('</untrusted_issue>', '')
        title = (self.issue.get('title') or '').replace('</untrusted_issue>', '')
        return f'<untrusted_issue>\nTitle: {title}\n\n{body}\n</untrusted_issue>'

    def stage_spec(self):
        feedback = ''
        for attempt in range(1, config.MAX_STAGE_TRIES + 1):
            t0 = time.time()
            tree = self.fresh_tree(f'analyst_spec_{attempt}')
            skill = tree / '_autose_skill'
            skill.mkdir()
            shutil.copy(self.repo / 'workflow/skills/requirements-spec-builder/SKILL.md', skill / 'SKILL.md')
            task = (f'GitHub issue #{self.issue_no}:\n{self.issue_block()}\n\n'
                    f'Write the specification to _autose_out/spec.md.{feedback}')
            run = agents.run_agent('analyst', 'analyst_spec', task, tree,
                                   self.out / 'trajectories' / f'analyst_spec_{attempt}.json')
            self.agent_ran('1-requirements', run)
            self.enforce_writes('analyst', tree)
            spec_path = tree / '_autose_out/spec.md'
            text = spec_path.read_text() if spec_path.exists() else ''
            gate = checks.check_spec(text)
            self.write('spec.md', text or '(no spec was written)\n')
            if gate.ok:
                self.record('1-requirements', 'pass', f'{len(gate.data["acs"])} acceptance criteria, '
                            f'verdict {gate.data["verdict"]}', attempt=attempt, agent=run,
                            seconds=round(time.time() - t0))
                return text, gate.data['acs']
            if gate.data.get('verdict') == 'NOT-READY':
                break   # a person must answer first; retrying will not help
            feedback = '\n\nYour previous spec failed the automatic check:\n- ' + '\n- '.join(gate.problems)
        self.write('spec.md', text + '\n\n## Gate result (stage 1)\n\n' + gate.summary() + '\n')
        raise Stop('1-requirements', gate.summary())

    def arch_context(self):
        if self.args.arch_context == 'map':
            return (self.repo / 'workflow/context/architecture_map.md').read_text()
        return (self.repo / 'ARCHITECTURE.md').read_text()

    def stage_design(self, spec, extra_feedback=''):
        feedback = extra_feedback
        for attempt in range(1, config.MAX_STAGE_TRIES + 1):
            t0 = time.time()
            tree = self.fresh_tree(f'analyst_design_{attempt}_{int(t0)}', {
                'spec.md': spec, 'architecture.md': self.arch_context()})
            task = (f'Plan the change for GitHub issue #{self.issue_no}. The issue for reference:\n'
                    f'{self.issue_block()}\n\nWrite _autose_out/design.md.{feedback}')
            run = agents.run_agent('analyst', 'analyst_design', task, tree,
                                   self.out / 'trajectories' / f'analyst_design_{attempt}_{int(t0)}.json')
            self.agent_ran('2-design', run)
            self.enforce_writes('analyst', tree)
            path = tree / '_autose_out/design.md'
            text = path.read_text() if path.exists() else ''
            gate = checks.check_design(text, self.base)
            self.write('design.md', text or '(no design was written)\n')
            if gate.ok:
                self.record('2-design', 'pass', 'plans ' + ', '.join(gate.data['planned']),
                            attempt=attempt, agent=run, seconds=round(time.time() - t0))
                return text, gate.data['planned']
            feedback = (extra_feedback + '\n\nYour previous design failed the automatic check:\n- '
                        + '\n- '.join(gate.problems))
        self.write('design.md', text + '\n\n## Gate result (stage 2)\n\n' + gate.summary() + '\n')
        raise Stop('2-design', gate.summary())

    def stage_tests(self, spec, acs):
        feedback = ''
        for attempt in range(1, config.MAX_STAGE_TRIES + 1):
            t0 = time.time()
            tree = self.fresh_tree(f'test_author_{attempt}', {'spec.md': spec})
            task = (f'Write the acceptance tests to {self.test_file}. Acceptance criteria ids: '
                    f'{", ".join(acs)}.{feedback}')
            run = agents.run_agent('test_author', 'test_author', task, tree,
                                   self.out / 'trajectories' / f'test_author_{attempt}.json')
            self.agent_ran('4a-tests', run)
            self.enforce_writes('test_author', tree)
            extra = [p for p in sandbox.changed_files(self.base, tree)['added']
                     if p.startswith('tests/') and p != self.test_file]
            for p in extra:
                sandbox.revert(self.base, tree, p)
            gate = checks.check_red(tree, self.test_file, acs)
            src = tree / self.test_file
            if src.exists():
                self.write(Path(self.test_file).name, src.read_text())
            if gate.ok:
                self.record('4a-tests', 'pass', f'{len(gate.data["tests"])} new tests, all red on base',
                            attempt=attempt, agent=run, seconds=round(time.time() - t0))
                return src.read_text()
            feedback = '\n\nYour previous tests failed the automatic check:\n- ' + '\n- '.join(gate.problems)
        raise Stop('4a-tests', gate.summary())

    def build_loop(self, spec, design, planned, tests_src, acs, review_feedback=''):
        attempt, prev_sig, feedback = 0, None, review_feedback
        tree = None
        report = []
        while True:
            attempt += 1
            t0 = time.time()
            files = {'spec.md': spec, 'design.md': design}
            if feedback:
                files['feedback.md'] = feedback
            if tree is None:
                tree = self.fresh_tree(f'builder_{attempt}_{int(t0)}', files)
            else:
                for k, v in files.items():
                    (tree / '_autose_out' / k).write_text(v)
            task = (f'Implement GitHub issue #{self.issue_no} as specified.' +
                    ('\n\nRead _autose_out/feedback.md first: it explains why the previous attempt '
                     'was not accepted.' if feedback else ''))
            run = agents.run_agent('builder', 'builder', task, tree,
                                   self.out / 'trajectories' / f'builder_{attempt}_{int(t0)}.json')
            self.agent_ran('3-implementation', run)
            reverted = self.enforce_writes('builder', tree)
            changed = sandbox.changed_files(self.base, tree)
            build = checks.check_build(tree, changed, planned)
            self.write('diff.patch', sandbox.unified_diff(
                self.base, tree, changed['added'] + changed['modified'] + changed['deleted']))
            entry = {'attempt': attempt, 'reverted': reverted, 'build': build.summary(), 'agent': run}
            if build.ok:
                self.record('3-implementation', 'pass', 'builds; touched ' + ', '.join(build.data['touched']),
                            attempt=attempt, agent=run, reverted=reverted, seconds=round(time.time() - t0))
                eval_tree = WORK / f'eval_{attempt}_{int(t0)}'
                if eval_tree.exists():
                    shutil.rmtree(eval_tree)
                shutil.copytree(tree, eval_tree)
                (eval_tree / self.test_file).write_text(tests_src)
                green = checks.check_green(eval_tree, self.test_file, acs)
                entry['tests'] = {'passed': green.data['passed'], 'total': green.data['total'],
                                  'failing': list(green.data['failing'])}
                report.append(entry)
                if green.ok:
                    self.write('test_report.md', self.test_report(report, green))
                    self.record('4b-testing', 'pass',
                                f'{green.data["passed"]}/{green.data["total"]} tests pass', attempts=attempt)
                    return tree, changed
                sig = green.data['signature']
                feedback = ('These tests failed after your change (names and error messages only):\n' +
                            '\n'.join(f'- {t.split("::")[-1]}: {r["message"]}'
                                      for t, r in green.data['failing'].items()))
                self.record('4b-testing', 'retry', f'{len(green.data["failing"])} failing (attempt {attempt})')
            else:
                report.append(entry)
                sig = ('build', tuple(build.problems))
                feedback = 'Your change did not pass the build check:\n- ' + '\n- '.join(build.problems)
                if reverted:
                    feedback += '\nThese changes were reverted because you may not edit them: ' + ', '.join(reverted)
                self.record('3-implementation', 'retry', build.summary()[:200], attempt=attempt,
                            agent=run, reverted=reverted)
            self.write('test_report.md', self.test_report(report, None))

            if sig == prev_sig and self.st.design_escalations < config.MAX_DESIGN_ESCALATIONS:
                # Same failure twice: the plan is probably wrong (ADR-009 stuck detection)
                self.st.design_escalations += 1
                design, planned = self.stage_design(
                    spec, '\n\nThe previous plan led to the same failure twice. Change the plan.\n' + feedback)
                tree, prev_sig = None, None
                continue
            if attempt >= config.MAX_BUILD_ATTEMPTS:
                raise Stop('4b-testing', f'tests still failing after {attempt} attempts')
            prev_sig = sig

    def test_report(self, report, green):
        lines = ['# Test report', '']
        for e in report:
            t = e.get('tests')
            lines.append(f"- attempt {e['attempt']}: build {e['build']}"
                         + (f"; tests {t['passed']}/{t['total']} pass" if t else '')
                         + (f"; reverted {', '.join(e['reverted'])}" if e['reverted'] else ''))
            if t and t['failing']:
                lines += [f'  - failing: {f}' for f in t['failing'][:20]]
        if green:
            lines += ['', '## Acceptance tests (new)', '']
            lines += [f"- {t.split('::')[-1]}: {r['outcome']}" for t, r in sorted(green.data['new_tests'].items())]
            lines += ['', f"Full suite: {green.data['passed']}/{green.data['total']} passed."]
        return '\n'.join(lines) + '\n'

    # --- stage 5 -------------------------------------------------------------------

    def git(self, *args):
        return subprocess.run(['git', *args], cwd=self.repo, check=True, capture_output=True, text=True).stdout

    def stage_release(self, spec, acs, tree, changed, tests_src):
        t0 = time.time()
        branch = f'autose/issue-{self.issue_no}'
        self.git('config', 'user.name', 'github-actions[bot]')
        self.git('config', 'user.email', '41898282+github-actions[bot]@users.noreply.github.com')
        self.git('fetch', 'origin', 'master')
        self.git('checkout', '-B', branch, 'origin/master')
        paths = changed['added'] + changed['modified']
        for rel in paths:
            dst = self.repo / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(tree / rel, dst)
        for rel in changed['deleted']:
            (self.repo / rel).unlink(missing_ok=True)
        (self.repo / self.test_file).write_text(tests_src)
        self.git('add', '--', *paths, *changed['deleted'], self.test_file)
        title = self.issue.get('title', '')
        self.git('commit', '-m', f'AutoSE: {title} (#{self.issue_no}, round {self.args.round})')
        sha = self.git('rev-parse', 'HEAD').strip()
        subprocess.run(['gh', 'auth', 'setup-git'], check=True)
        self.git('push', '--force', 'origin', f'HEAD:refs/heads/{branch}')

        body = self.pr_body(spec, acs, changed)
        self.write('pr.md', body)
        pr = gh.find_pr_for_branch(branch)
        if pr:
            gh.update_pr(pr['number'], body)
        else:
            pr = gh.create_pr(branch, 'master', f'AutoSE: {title}', body)
        self.st.pr, self.st.branch = pr['number'], branch

        gh.dispatch(CI_WORKFLOW, branch, {})
        ci = gh.wait_for_ci(CI_WORKFLOW, branch, sha, config.CI_WAIT_SECONDS)
        with open(self.out / 'pr.md', 'a') as f:
            f.write(f"\n\nPR: {pr['html_url']}\nCI: {ci['conclusion']} {ci['url']}\n")
        if ci['conclusion'] != 'success':
            raise Stop('5-release', f"PR #{pr['number']} is open but CI is {ci['conclusion']}: {ci['url']}")
        self.record('5-release', 'pass', f"PR #{pr['number']} open, CI green", pr=pr['number'],
                    ci=ci['url'], seconds=round(time.time() - t0))
        return pr

    def pr_body(self, spec, acs, changed):
        files = changed['added'] + changed['modified'] + changed['deleted']
        rows = '\n'.join(f'| {ac} | `{checks.ac_test_token(ac)}` in `{self.test_file}` | {", ".join(files)} |'
                         for ac in acs)
        return (f'Closes #{self.issue_no}\n\n'
                f'Opened by the AutoSE workflow (review round {self.args.round}). '
                f'An independent reviewer will comment below. **A person decides whether to merge.**\n\n'
                f'## Traceability\n\n| Acceptance criterion | Test | Files changed |\n|---|---|---|\n{rows}\n\n'
                f'Artifacts (spec, design, diff, test report): {gh.run_url()}\n')

    # --- main --------------------------------------------------------------------

    def load_previous(self):
        """For review rounds: reuse spec, design and tests from the previous run's artifact."""
        prev = WORK / 'prev'
        if prev.exists():
            shutil.rmtree(prev)
        prev.mkdir()
        gh.gh('run', 'download', str(self.args.prev_run_id), '--repo', gh.REPO, '--dir', str(prev))
        found = {}
        for p in prev.rglob('*'):
            if p.is_file():
                found.setdefault(p.name, p.read_text())
        return found

    def main(self):
        self.st = state.load(self.issue_no)
        self.st.round, self.st.status, self.st.note = self.args.round, 'running', ''
        self.st.runs.append({'round': self.args.round, 'run_url': gh.run_url(), 'result': 'running'})
        state.save(self.st)
        self.issue = gh.get_issue(self.issue_no)
        self.base = sandbox.make_tree(self.repo, WORK / 'base')
        os.chmod(self.base, 0o755)
        resume = self.args.resume_from
        try:
            prev = self.load_previous() if resume > 1 else {}
            review_feedback = prev.get('review.md', '')
            if resume <= 1:
                spec, acs = self.stage_spec()
            else:
                spec = prev['spec.md']
                acs = checks.check_spec(spec).data['acs']
                self.write('spec.md', spec)
            if resume <= 2:
                fb = ('\n\nThe independent reviewer asked for a different approach:\n' + review_feedback
                      if review_feedback else '')
                design, planned = self.stage_design(spec, fb)
            else:
                design = prev['design.md']
                planned = checks.check_design(design, self.base).data['planned']
                self.write('design.md', design)
            tests_name = Path(self.test_file).name
            if resume <= 1 or tests_name not in prev:
                tests_src = self.stage_tests(spec, acs)
            else:
                tests_src = prev[tests_name]
                self.write(tests_name, tests_src)
            fb = ('The independent reviewer requested these changes:\n' + review_feedback
                  if review_feedback and resume == 3 else '')
            tree, changed = self.build_loop(spec, design, planned, tests_src, acs, fb)
            if self.args.stop_after <= 4:
                self.st.status = 'stopped'
                self.st.note = 'experiment run: stopped after stage 4 as requested'
                self.finish('stopped-after-4')
                return 'stopped-after-4'
            pr = self.stage_release(spec, acs, tree, changed, tests_src)
            self.st.status = 'pr_open'
            self.finish('pr_open', pr=pr['number'])
            return 'pr_open'
        except Stop as s:
            self.st.status, self.st.note = 'stopped', f'stage {s.stage}: {s.reason}'
            self.results['stopped'] = {'stage': s.stage, 'reason': s.reason}
            gh.add_labels(self.issue_no, [config.LABEL_FAILED])
            self.finish('stopped')
            return 'stopped'

    def finish(self, result, pr=0):
        self.st.runs[-1]['result'] = result
        self.st.tokens = {r: u.total for r, u in agents.USAGE.items()}
        state.save(self.st)
        self.results['result'] = result
        self.dump()
        out = os.environ.get('GITHUB_OUTPUT')
        if out:
            with open(out, 'a') as f:
                f.write(f'status={result}\npr={pr or self.st.pr}\nissue={self.issue_no}\n')


def parse_args(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--issue', type=int, required=True)
    p.add_argument('--round', type=int, default=0)
    p.add_argument('--resume-from', type=int, default=1, choices=[1, 2, 3])
    p.add_argument('--prev-run-id', default='')
    p.add_argument('--arch-context', default='full', choices=['full', 'map'])
    p.add_argument('--stop-after', type=int, default=5, choices=[4, 5])
    p.add_argument('--out', default='out')
    return p.parse_args(argv)


if __name__ == '__main__':
    import sys
    # A stopped run must show as failed (red) in the Actions list, not green.
    sys.exit(1 if Run(parse_args()).main() == 'stopped' else 0)
