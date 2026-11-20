"""Stage 6, part 2: publish the review and route the next step (ADR-002).

Runs in a separate job that holds the write permissions the Reviewer job
does not have. It only reads ``review_result.json`` / ``review.md``.

- APPROVE         -> label "ready-for-human"; a person merges or closes.
- REQUEST_CHANGES -> if another round is allowed: dispatch a new workflow run that
                     resumes at stage 2 (approach) or 3 (code); else "needs-human".
- INCONCLUSIVE    -> label "needs-human".
Experiment reviews (seeded PRs) only post the comment.

Usage:
    python -m autose.post_review --dir review_out/ [--experiment]
"""
import argparse
import json
import os
from pathlib import Path

from . import config, gh, state


def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument('--dir', default='review_out')
    p.add_argument('--experiment', action='store_true')
    args = p.parse_args(argv)
    d = Path(args.dir)
    result = json.loads((d / 'review_result.json').read_text())
    body = (d / 'review.md').read_text()
    pr, issue, rnd = result['pr'], result['issue'], result['round']
    gh.gh('pr', 'comment', str(pr), '--repo', gh.REPO, '--body-file', str(d / 'review.md'))
    if args.experiment:
        return

    st = state.load(issue)
    st.stages['6-review'] = {'status': result['verdict'], 'summary': result['reason']}
    st.stage = '6-review'
    verdict = result['verdict']
    if verdict == 'APPROVE':
        st.status = 'approved'
        gh.add_labels(issue, [config.LABEL_READY])
        gh.add_labels(pr, [config.LABEL_READY])
    elif verdict == 'REQUEST_CHANGES' and rnd + 1 < config.MAX_REVIEW_ROUNDS:
        resume = 2 if result['route'] == 'approach' else 3
        st.status = 'running'
        st.note = f'review round {rnd} asked for changes ({result["route"]}); round {rnd + 1} resumes at stage {resume}'
        gh.dispatch('autose.yml', 'master', {
            'issue': issue, 'round': rnd + 1, 'resume_from': resume,
            'prev_run_id': os.environ.get('GITHUB_RUN_ID', ''),
        })
    else:
        st.status = 'needs_human'
        st.note = ('review rounds used up' if verdict == 'REQUEST_CHANGES'
                   else f'review inconclusive: {result["reason"]}')
        gh.add_labels(issue, [config.LABEL_NEEDS_HUMAN])
        gh.add_labels(pr, [config.LABEL_NEEDS_HUMAN])
    if st.runs:
        st.runs[-1]['result'] = f'review: {verdict}'
    state.save(st)
    print(body)


if __name__ == '__main__':
    main()
