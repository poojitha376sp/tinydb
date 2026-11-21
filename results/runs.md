# Runs

Every GitHub Actions run, pull request and review used in the report. Generated from the
downloaded run artifacts (`stage_results.json`, `review_result.json`); the same rows are in
[results.csv](results.csv). Hidden tests were run outside the repository on each build diff.
Stage names: 1 requirements, 2 design, 4a tests written, 3 implementation, 4b testing, 5 release.

## Issue runs (Part 4: all five issues)

| Task | Issue | Run | Result | Stopped at | Stages passed | Retries | Tokens | Hidden tests | PR |
|---|---|---|---|---|---|---|---|---|---|
| I1 | [#3](https://github.com/poojitha376sp/tinydb/issues/3) | [44690536504](https://github.com/poojitha376sp/tinydb/actions/runs/44690536504) | stopped | 1: FAIL: missing "Verdict: READY/PARTIALLY-READY/NOT-READY" line; no requirement lines of the |  | 0 | 0 |  |  |
| I1 | [#3](https://github.com/poojitha376sp/tinydb/issues/3) | [44691931258](https://github.com/poojitha376sp/tinydb/actions/runs/44691931258) | stopped | 1: FAIL: missing "Verdict: READY/PARTIALLY-READY/NOT-READY" line; no requirement lines of the |  | 0 | 0 |  |  |
| I1 | [#3](https://github.com/poojitha376sp/tinydb/issues/3) | [44692766501](https://github.com/poojitha376sp/tinydb/actions/runs/44692766501) | stopped | 1: Error: ServiceUnavailableError |  | 0 | 114394 |  |  |
| I1 | [#3](https://github.com/poojitha376sp/tinydb/issues/3) | [44739862609](https://github.com/poojitha376sp/tinydb/actions/runs/44739862609) | incomplete |  | 1 2 | 1 | 430411 |  |  |
| I1 | [#3](https://github.com/poojitha376sp/tinydb/issues/3) | [44777819084](https://github.com/poojitha376sp/tinydb/actions/runs/44777819084) | pr_open |  | 1 2 4a 3 4b 5 | 0 | 197640 | 3/3 | [#7](https://github.com/poojitha376sp/tinydb/pull/7) |
| I2 | [#9](https://github.com/poojitha376sp/tinydb/issues/9) | [44790247695](https://github.com/poojitha376sp/tinydb/actions/runs/44790247695) | stopped | 1: FAIL: AC-FR001-a has no observable expected result after "->"; AC-FR002-a has no observabl |  | 0 | 137331 |  |  |
| I2 | [#9](https://github.com/poojitha376sp/tinydb/issues/9) | [44816038999](https://github.com/poojitha376sp/tinydb/actions/runs/44816038999) | pr_open |  | 1 2 4a 3 4b 5 | 1 | 169840 | 3/3 | [#12](https://github.com/poojitha376sp/tinydb/pull/12) |
| I3 | [#10](https://github.com/poojitha376sp/tinydb/issues/10) | [44790279547](https://github.com/poojitha376sp/tinydb/actions/runs/44790279547) | stopped | 4b: 1 failing (attempt 3) | 1 2 4a 3 | 2 | 788524 | 4/4 |  |
| I3 | [#10](https://github.com/poojitha376sp/tinydb/issues/10) | [44819950934](https://github.com/poojitha376sp/tinydb/actions/runs/44819950934) | stopped | 4b: 1 failing (attempt 3) | 1 2 4a 3 | 3 | 386590 | 4/4 |  |
| I3 | [#10](https://github.com/poojitha376sp/tinydb/issues/10) | [44874308479](https://github.com/poojitha376sp/tinydb/actions/runs/44874308479) | pr_open |  | 1 2 4a 3 4b 5 | 0 | 289956 | 4/4 | [#19](https://github.com/poojitha376sp/tinydb/pull/19) |
| I4 | [#14](https://github.com/poojitha376sp/tinydb/issues/14) | [44821760207](https://github.com/poojitha376sp/tinydb/actions/runs/44821760207) | pr_open |  | 1 2 4a 3 4b 5 | 1 | 228056 | 3/3 | [#15](https://github.com/poojitha376sp/tinydb/pull/15) |
| I5 | [#18](https://github.com/poojitha376sp/tinydb/issues/18) | [44874333544](https://github.com/poojitha376sp/tinydb/actions/runs/44874333544) | stopped | 1: FAIL: the spec says NOT-READY: the issue cannot be specified without answers from a person |  | 0 | 61843 |  |  |

## Reviews of the issue PRs (stage 6, independent reviewer)

| Task | PR | Run | Verdict | Steps | Tokens | Models | Note |
|---|---|---|---|---|---|---|---|
| I1 | [#7](https://github.com/poojitha376sp/tinydb/pull/7) | [44777819084](https://github.com/poojitha376sp/tinydb/actions/runs/44777819084) | INCONCLUSIVE | 1 | 0 |  | no valid verdict in review.json |
| I1 | [#7](https://github.com/poojitha376sp/tinydb/pull/7) | [44788824929](https://github.com/poojitha376sp/tinydb/actions/runs/44788824929) | APPROVE | 17 | 67582 | gpt-oss-120b qwen3.8-27b | no must-fix findings, break-it test run, scores >= 7 |
| I2 | [#12](https://github.com/poojitha376sp/tinydb/pull/12) | [44816038999](https://github.com/poojitha376sp/tinydb/actions/runs/44816038999) | INCONCLUSIVE | 3 | 6949 | gpt-oss-120b | no valid verdict in review.json |
| I2 | [#12](https://github.com/poojitha376sp/tinydb/pull/12) | [44819910385](https://github.com/poojitha376sp/tinydb/actions/runs/44819910385) | INCONCLUSIVE | 20 | 80865 | gpt-oss-120b qwen3.8-27b | claimed APPROVE; approval without a break-it test that was actually run |
| I2 | [#12](https://github.com/poojitha376sp/tinydb/pull/12) | [44874280785](https://github.com/poojitha376sp/tinydb/actions/runs/44874280785) | INCONCLUSIVE | 20 | 82287 | gpt-oss-120b qwen3.8-27b | no valid verdict in review.json |
| I2 | [#12](https://github.com/poojitha376sp/tinydb/pull/12) | [44880309740](https://github.com/poojitha376sp/tinydb/actions/runs/44880309740) | APPROVE | 12 | 43146 | gpt-oss-120b qwen3.8-27b | no must-fix findings, break-it test run, scores >= 7 |
| I3 | [#19](https://github.com/poojitha376sp/tinydb/pull/19) | [44874308479](https://github.com/poojitha376sp/tinydb/actions/runs/44874308479) | APPROVE | 19 | 77310 | gpt-oss-120b qwen3.8-27b | no must-fix findings, break-it test run, scores >= 7 |
| I4 | [#15](https://github.com/poojitha376sp/tinydb/pull/15) | [44821760207](https://github.com/poojitha376sp/tinydb/actions/runs/44821760207) | INCONCLUSIVE | 1 | 3588 | gpt-oss-120b | no valid verdict in review.json |
| I4 | [#15](https://github.com/poojitha376sp/tinydb/pull/15) | [44880091825](https://github.com/poojitha376sp/tinydb/actions/runs/44880091825) | INCONCLUSIVE | 4 | 15674 | gpt-oss-120b qwen3.8-27b | claimed APPROVE; approval without a break-it test that was actually run |
| I4 | [#15](https://github.com/poojitha376sp/tinydb/pull/15) | [44881304977](https://github.com/poojitha376sp/tinydb/actions/runs/44881304977) | INCONCLUSIVE | 6 | 22368 | gpt-oss-120b qwen3.8-27b | claimed APPROVE; approval without a break-it test that was actually run |
| I4 | [#15](https://github.com/poojitha376sp/tinydb/pull/15) | [44893115338](https://github.com/poojitha376sp/tinydb/actions/runs/44893115338) | INCONCLUSIVE | 20 | 157719 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| I4 | [#15](https://github.com/poojitha376sp/tinydb/pull/15) | [44896136737](https://github.com/poojitha376sp/tinydb/actions/runs/44896136737) | APPROVE | 23 | 259267 | nemotron-3-ultra-550b-a55b | no must-fix findings, break-it test run, scores >= 7 |

## E1: reviewer independence on the five seeded PRs

Correct verdict: S1 APPROVE, S2 to S5 REQUEST_CHANGES.

| PR | Variant | Trial | Run | Verdict | Expected | Correct | Steps | Tokens | Models | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | baseline | 1 | [44882116757](https://github.com/poojitha376sp/tinydb/actions/runs/44882116757) | APPROVE | APPROVE | yes | 8 | 64614 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | baseline | 1 | [44881995342](https://github.com/poojitha376sp/tinydb/actions/runs/44881995342) | APPROVE | REQUEST_CHANGES | no (false approval) | 3 | 17573 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | baseline | 1 | [44881873171](https://github.com/poojitha376sp/tinydb/actions/runs/44881873171) | APPROVE | REQUEST_CHANGES | no (false approval) | 6 | 49584 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | baseline | 1 | [44881709783](https://github.com/poojitha376sp/tinydb/actions/runs/44881709783) | APPROVE | REQUEST_CHANGES | no (false approval) | 12 | 122866 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | baseline | 1 | [44881578737](https://github.com/poojitha376sp/tinydb/actions/runs/44881578737) | APPROVE | REQUEST_CHANGES | no (false approval) | 3 | 18930 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | baseline | 2 | [44882731275](https://github.com/poojitha376sp/tinydb/actions/runs/44882731275) | APPROVE | APPROVE | yes | 5 | 35444 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | baseline | 2 | [44882597126](https://github.com/poojitha376sp/tinydb/actions/runs/44882597126) | APPROVE | REQUEST_CHANGES | no (false approval) | 6 | 41935 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | baseline | 2 | [44882496078](https://github.com/poojitha376sp/tinydb/actions/runs/44882496078) | APPROVE | REQUEST_CHANGES | no (false approval) | 5 | 35987 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | baseline | 2 | [44882374328](https://github.com/poojitha376sp/tinydb/actions/runs/44882374328) | APPROVE | REQUEST_CHANGES | no (false approval) | 3 | 18982 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | baseline | 2 | [44882252698](https://github.com/poojitha376sp/tinydb/actions/runs/44882252698) | APPROVE | REQUEST_CHANGES | no (false approval) | 3 | 4823 | gemini-3.5-flash-lite | baseline variant: verdict taken as given |
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | independent | 1 | [44896124333](https://github.com/poojitha376sp/tinydb/actions/runs/44896124333) | APPROVE | APPROVE | yes | 16 | 77539 | nemotron-3-ultra-550b-a55b | no must-fix findings, break-it test run, scores >= 7 |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | independent | 1 | [44896332497](https://github.com/poojitha376sp/tinydb/actions/runs/44896332497) | REQUEST_CHANGES | REQUEST_CHANGES | yes | 32 | 340750 | nemotron-3-ultra-550b-a55b | 2 must-fix finding(s) with evidence |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | independent | 1 | [44896633895](https://github.com/poojitha376sp/tinydb/actions/runs/44896633895) | INCONCLUSIVE | REQUEST_CHANGES | no | 40 | 479846 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | independent | 1 | [44896989479](https://github.com/poojitha376sp/tinydb/actions/runs/44896989479) | INCONCLUSIVE | REQUEST_CHANGES | no | 40 | 511648 | nemotron-3-ultra-550b-a55b | claimed REQUEST_CHANGES; changes requested but no finding had evidence |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | independent | 1 | [44897483225](https://github.com/poojitha376sp/tinydb/actions/runs/44897483225) | REQUEST_CHANGES | REQUEST_CHANGES | yes | 40 | 521046 | nemotron-3-ultra-550b-a55b | 1 must-fix finding(s) with evidence |
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | independent | 2 | [44897896015](https://github.com/poojitha376sp/tinydb/actions/runs/44897896015) | APPROVE | APPROVE | yes | 14 | 80583 | nemotron-3-ultra-550b-a55b | no must-fix findings, break-it test run, scores >= 7 |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | independent | 2 | [44898092864](https://github.com/poojitha376sp/tinydb/actions/runs/44898092864) | INCONCLUSIVE | REQUEST_CHANGES | no | 5 | 10710 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | independent | 2 | [44898276252](https://github.com/poojitha376sp/tinydb/actions/runs/44898276252) | INCONCLUSIVE | REQUEST_CHANGES | no | 40 | 502355 | nemotron-3-ultra-550b-a55b | claimed REQUEST_CHANGES; changes requested but no finding had evidence |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | independent | 2 | [44898639758](https://github.com/poojitha376sp/tinydb/actions/runs/44898639758) | REQUEST_CHANGES | REQUEST_CHANGES | yes | 40 | 488100 | nemotron-3-ultra-550b-a55b | 1 must-fix finding(s) with evidence |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | independent | 2 | [44899126385](https://github.com/poojitha376sp/tinydb/actions/runs/44899126385) | INCONCLUSIVE | REQUEST_CHANGES | no | 40 | 591141 | nemotron-3-ultra-550b-a55b | claimed REQUEST_CHANGES; changes requested but no finding had evidence |

**baseline**: 2/10 correct; seeded defects caught 0/8, false approvals 8/8, INCONCLUSIVE 0; mean tokens 41074. Verdict the reviewer itself wrote on S2 to S5, before the evidence rules: REQUEST_CHANGES 0/8, APPROVE 8/8, none written 0/8.

**independent**: 5/10 correct; seeded defects caught 3/8, false approvals 0/8, INCONCLUSIVE 5; mean tokens 360372. Verdict the reviewer itself wrote on S2 to S5, before the evidence rules: REQUEST_CHANGES 6/8, APPROVE 0/8, none written 2/8.

## E1 pilot 1 (independent reviewer on Groq, stopped by the daily token quota)

Correct verdict: S1 APPROVE, S2 to S5 REQUEST_CHANGES.

| PR | Variant | Trial | Run | Verdict | Expected | Correct | Steps | Tokens | Models | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | independent | 1 | [44881790938](https://github.com/poojitha376sp/tinydb/actions/runs/44881790938) | APPROVE | APPROVE | yes | 17 | 61803 | gpt-oss-120b qwen3.8-27b | no must-fix findings, break-it test run, scores >= 7 |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | independent | 1 | [44882132462](https://github.com/poojitha376sp/tinydb/actions/runs/44882132462) | REQUEST_CHANGES | REQUEST_CHANGES | yes | 7 | 24014 | gpt-oss-120b qwen3.8-27b | 1 must-fix finding(s) with evidence |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | independent | 1 | [44882303209](https://github.com/poojitha376sp/tinydb/actions/runs/44882303209) | INCONCLUSIVE | REQUEST_CHANGES | no | 4 | 17065 | gpt-oss-120b qwen3.8-27b | claimed REQUEST_CHANGES; changes requested but no finding had evidence |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | independent | 1 | [44882451753](https://github.com/poojitha376sp/tinydb/actions/runs/44882451753) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 81429 | gpt-oss-120b qwen3.8-27b | no valid verdict in review.json |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | independent | 1 | [44882975499](https://github.com/poojitha376sp/tinydb/actions/runs/44882975499) | INCONCLUSIVE | REQUEST_CHANGES | no | 10 | 36173 | gpt-oss-120b qwen3.8-27b | no valid verdict in review.json |
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | independent | 2 | [44883413453](https://github.com/poojitha376sp/tinydb/actions/runs/44883413453) | INCONCLUSIVE | APPROVE | no | 2 | 1778 | qwen3.8-27b | no valid verdict in review.json |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | independent | 2 | [44883534958](https://github.com/poojitha376sp/tinydb/actions/runs/44883534958) | INCONCLUSIVE | REQUEST_CHANGES | no | 3 | 5150 | gpt-oss-120b qwen3.8-27b | no valid verdict in review.json |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | independent | 2 | [44883687666](https://github.com/poojitha376sp/tinydb/actions/runs/44883687666) | INCONCLUSIVE | REQUEST_CHANGES | no | 1 | 0 |  | no valid verdict in review.json |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | independent | 2 | [44883814058](https://github.com/poojitha376sp/tinydb/actions/runs/44883814058) | INCONCLUSIVE | REQUEST_CHANGES | no | 1 | 0 |  | no valid verdict in review.json |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | independent | 2 | [44883969509](https://github.com/poojitha376sp/tinydb/actions/runs/44883969509) | INCONCLUSIVE | REQUEST_CHANGES | no | 1 | 0 |  | no valid verdict in review.json |

**independent**: 2/10 correct; seeded defects caught 1/8, false approvals 0/8, INCONCLUSIVE 8; mean tokens 22741. Verdict the reviewer itself wrote on S2 to S5, before the evidence rules: REQUEST_CHANGES 2/8, APPROVE 0/8, none written 6/8.

## E1 pilot 2 (independent reviewer on NVIDIA Nemotron with the old 20-step limit)

Correct verdict: S1 APPROVE, S2 to S5 REQUEST_CHANGES.

| PR | Variant | Trial | Run | Verdict | Expected | Correct | Steps | Tokens | Models | Note |
|---|---|---|---|---|---|---|---|---|---|---|
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | independent | 1 | [44893106056](https://github.com/poojitha376sp/tinydb/actions/runs/44893106056) | INCONCLUSIVE | APPROVE | no | 20 | 148080 | nemotron-3-ultra-550b-a55b | claimed APPROVE; approval without a break-it test that was actually run |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | independent | 1 | [44893374487](https://github.com/poojitha376sp/tinydb/actions/runs/44893374487) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 97819 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | independent | 1 | [44893592450](https://github.com/poojitha376sp/tinydb/actions/runs/44893592450) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 210238 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | independent | 1 | [44893855893](https://github.com/poojitha376sp/tinydb/actions/runs/44893855893) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 177890 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | independent | 1 | [44894089142](https://github.com/poojitha376sp/tinydb/actions/runs/44894089142) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 263945 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S1 [#21](https://github.com/poojitha376sp/tinydb/pull/21) | independent | 2 | [44894303699](https://github.com/poojitha376sp/tinydb/actions/runs/44894303699) | INCONCLUSIVE | APPROVE | no | 20 | 110640 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S2 [#23](https://github.com/poojitha376sp/tinydb/pull/23) | independent | 2 | [44894535314](https://github.com/poojitha376sp/tinydb/actions/runs/44894535314) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 154287 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S3 [#25](https://github.com/poojitha376sp/tinydb/pull/25) | independent | 2 | [44894937912](https://github.com/poojitha376sp/tinydb/actions/runs/44894937912) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 176334 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S4 [#27](https://github.com/poojitha376sp/tinydb/pull/27) | independent | 2 | [44895133458](https://github.com/poojitha376sp/tinydb/actions/runs/44895133458) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 145130 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |
| S5 [#29](https://github.com/poojitha376sp/tinydb/pull/29) | independent | 2 | [44895377629](https://github.com/poojitha376sp/tinydb/actions/runs/44895377629) | INCONCLUSIVE | REQUEST_CHANGES | no | 20 | 268833 | nemotron-3-ultra-550b-a55b | no valid verdict in review.json |

**independent**: 0/10 correct; seeded defects caught 0/8, false approvals 0/8, INCONCLUSIVE 10; mean tokens 175320. Verdict the reviewer itself wrote on S2 to S5, before the evidence rules: REQUEST_CHANGES 0/8, APPROVE 0/8, none written 8/8.

## E2: full ARCHITECTURE.md vs short map (stages 1 to 4)

Issue copies #30 to #33 (I1 to I4) were opened without the autose label so only these runs touched them.

| Task | Variant | Trial | Issue | Run | Stages passed | Retries | Steps | Tokens | Hidden tests |
|---|---|---|---|---|---|---|---|---|---|
| I1 | full | 1 | [#30](https://github.com/poojitha376sp/tinydb/issues/30) | [44884513938](https://github.com/poojitha376sp/tinydb/actions/runs/44884513938) | 1 2 4a 3 4b | 1 | 25 | 185414 | 3/3 |
| I1 | map | 1 | [#30](https://github.com/poojitha376sp/tinydb/issues/30) | [44885907255](https://github.com/poojitha376sp/tinydb/actions/runs/44885907255) | 1 2 4a 3 4b | 0 | 26 | 176287 | 3/3 |
| I2 | full | 1 | [#31](https://github.com/poojitha376sp/tinydb/issues/31) | [44884809106](https://github.com/poojitha376sp/tinydb/actions/runs/44884809106) | 1 2 4a 3 4b | 1 | 31 | 189080 | 3/3 |
| I2 | map | 1 | [#31](https://github.com/poojitha376sp/tinydb/issues/31) | [44885672921](https://github.com/poojitha376sp/tinydb/actions/runs/44885672921) | 1 2 4a 3 4b | 0 | 26 | 117620 | 3/3 |
| I3 | full | 1 | [#32](https://github.com/poojitha376sp/tinydb/issues/32) | [44885229014](https://github.com/poojitha376sp/tinydb/actions/runs/44885229014) | 1 2 4a 3 4b | 2 | 25 | 236519 | 4/4 |
| I3 | map | 1 | [#32](https://github.com/poojitha376sp/tinydb/issues/32) | [44885229062](https://github.com/poojitha376sp/tinydb/actions/runs/44885229062) | 1 2 4a 3 4b | 0 | 28 | 151527 | 4/4 |
| I4 | full | 1 | [#33](https://github.com/poojitha376sp/tinydb/issues/33) | [44885472128](https://github.com/poojitha376sp/tinydb/actions/runs/44885472128) | 1 2 4a 3 4b | 1 | 30 | 252465 | 3/3 |
| I4 | map | 1 | [#33](https://github.com/poojitha376sp/tinydb/issues/33) | [44884516847](https://github.com/poojitha376sp/tinydb/actions/runs/44884516847) | 1 2 4a 3 4b | 1 | 47 | 389620 | 3/3 |

**full**: hidden tests all passed in 4/4 runs; mean tokens 215870, mean retries 1.25, mean steps 28.

**map**: hidden tests all passed in 4/4 runs; mean tokens 208764, mean retries 0.25, mean steps 32.
