# When the author reviews their own change

Two Leads each implemented a change to CDD's fictional reading desk. Each Lead then reviewed their own commit in the same session. A Guardian opened a fresh session for each commit. Both reviewers reached the reference decision on both changes. The Guardian contributed a second opinion and found no additional violation in this pair.

| Authored change | Decisive public behavior | Lead, initial → final | Guardian, initial → final | Lead time | Guardian time |
| --- | --- | --- | --- | ---: | ---: |
| `resume` reopens an unfinished entry | The output matches `open`, including `marks_complete=false` and `suggestions_visible=false`. | GO → GO | GO → GO | 47.5 s | 52.5 s |
| `pause` shows suggested reading immediately | `pause` returns `suggestions_visible=true` without a request. R-02 requires an explicit request. | NO-GO → NO-GO | NO-GO → NO-GO | 40.6 s | 48.3 s |

Each time is the sum of two separately measured review stages. Timing starts at dispatch and ends when the reviewer records the answer on the same host's monotonic clock. It includes scheduling, tool calls and Guardian startup. Implementation, the gap between stages and subsequent v0.4 record writing fall outside the interval. The review sessions used the same hosted defaults. The runner supplied neither a model build identifier nor token counts. Human review minutes were also unmeasured. The 8,000-token reporting threshold therefore has unknown status.

## What the comparison establishes

Both roles cited the same observable R-02 violation before the author's explanation. The implementing Lead had already flagged it in the handoff. Both roles accepted the compliant change. For each role, that gives one detection in one violating case and zero false blocks in one compliant case. The conditions for calculating the shared-miss rate occurred zero times. That rate is undefined. The eight observations are repeated decisions on two changes.

The conflict was written into the `pause` ticket deliberately. This exercises detection of explicit disagreement with an established rule. It leaves open whether a Guardian catches subtle mistakes that the author actually misses, or how often a second review pays for its time in routine work. A follow-on with naturally occurring changes and a reference reviewer who sees neither arm's decision would address that question.

## How the observations were collected

1. The operator committed both tasks, the scoring rule and the timing policy before commissioning code. Both authors received the same four-file product base and could read the corpus. They made their own local Git commits. The patches and original Git objects are archived here. [Preregistered plan](plan.json)
2. The operator matched each author session to its reported commit, executed all six existing actions plus the new action and froze the reference labels before review. All six existing actions preserved their outputs on both candidates. An additional engineering check changed the caption, library link and information labels. `resume` and `open` still agreed. This extra check was outside the shared review packets. [Results and original observations](results.json)
3. Each pair received the same task, base sources, diff, default-policy CLI outputs and decision format. The Guardian also received the CDD role instructions. Reviewers used separate contexts and were directed to read only their assigned packet. The shared host did not enforce filesystem isolation between packets. The Lead retained its implementation history. The two arms started in opposite orders across the two cases and could run concurrently.
4. Both initial decisions were locked before either arm received the same author's recorded explanation. Each reviewer continued in its original session. The operator supplied the reference labels from the preregistered rule and runtime evidence. Independent human adjudication remains open.

## v0.4 decision records

After scoring, the operator froze a separate context for each change, and the same Guardians wrote full v0.4 example verdicts. Each context ties the candidate, corpus, evaluator and expected scope to observations from seven public actions. The `resume` verdict records 19 clause assessments. The `pause` verdict records 15, including the R-02 BLOCK. Both records passed the example checker. This extra exercise is outside the paired timing and scores. Both corpora and their authority are fictional.

| Candidate | Authored patch | Independent context | Guardian verdict |
| --- | --- | --- | --- |
| `resume` | [Patch](resume/change.patch) | [Seven actions](resume/context.json) | [GO](resume/verdict.json) |
| `pause` | [Patch](pause/change.patch) | [Seven actions](pause/context.json) | [NO-GO](pause/verdict.json) |

## Reproduce the observations

From the repository root, using Python 3.10+ and Git, run the command below. It reconstructs the original candidate commits in a temporary directory, executes the public reader, verifies the source and evidence hashes, checks both v0.4 records and scores the eight archived responses. Model calls are unnecessary for replay.

```sh
python3 -B experiments/phase0/authored-pilot/replay.py
```
