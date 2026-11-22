# Running a Phase 0 shadow review

Use this lab to answer a narrow question. On the same change and accepted sources, does a separate Guardian detect something that another reviewer or the implementing Lead misses? The lab records observations in a local SQLite database. Product approval, human identity and merge permissions belong to the product's own workflow. Python 3.10+ and Git are sufficient.

## Try the included cases

Run from the repository root.

```sh
python3 experiments/phase0/lab.py smoke
python3 experiments/phase0/lab.py replay-sample
```

The first command feeds reference observations through the collector. It exercises 11 cases, 9 change families and 22 records without calling a model. The second regenerates the packets and scores eight [archived observations](observed-sample.json) from four actual review conversations on two deliberately selected cases. One case contains both an explicit violation and a missing source. In the other case a suspicious-looking setting preserves the public behavior. Both reviewers matched both reference labels before and after the author replied. The sessions yielded no model-version or usage telemetry. The reference labels were seeded by the case author. This sample demonstrates the workflow. It cannot estimate comparative performance.

## Exercise the v0.4 decision record

Run `python3 experiments/phase0/record_demo.py` from the repository root. Add `--out /path/to/new/folder` to retain the JSON and source snapshots. The exercise runs the reading desk's actual `open` and `library` actions. A Lead tracks the shared-shelf norm request. The initial result is HOLD. A separate candidate with unsolicited suggestions produces NO-GO while the same norm request remains open. A simulated Master event and a fresh review on the revised corpus produce GO for the compliant candidate. Omitting a required assessment, substituting the tracker for the deciding principal, or reusing the old verdict fails the checker.

Read the resulting [example verdict](../../examples/reading-desk/v0.4/verdict.json) and [its independent context](../../examples/reading-desk/v0.4/context.json) side by side. These records exercise the [v0.4 contract](../../skills/cdd-guardian/references/decision-record-v0.4.md). The compact model observations from the earlier v0.3 pilot keep their original meaning.

## Run a new comparison

Keep the operator directory outside the candidate's checkout. Set the same model version, reasoning settings, tool access and total additional-review budget for both arms. Capture the actual usage as well. The numeric token budget in the plan is a reporting threshold. Enforce a hard limit in the agent runner if the experiment requires one.

```sh
work_root=$(mktemp -d)
lab=experiments/phase0/lab.py
python3 "$lab" prepare "$work_root/run" --split evaluation --seed 17 --token-budget 8000
python3 "$lab" list "$work_root/run"
python3 "$lab" export "$work_root/run" t001 guardian --out "$work_root/reading-desk"
python3 "$lab" export "$work_root/run" t001 baseline --out "$work_root/book-desk"
```

1. Give each reviewer just its own export, in a separate, fresh context. Use generic directory names. Ask it to complete `ASSIGNMENT.md` and return one object using `response-format.md`. The same codebook, original task, effective base sources, candidate diff and measured public outputs go to both arms. The Guardian also receives the CDD role and skill. The operator-only `first_arm` is a randomized starting order for sequential runs. Collect model configuration, prior consultation and timings in the runner.
2. For the built-in reader, reproduce the behavior with `python3 reader.py open` inside the export. Compare alternate actions such as `preview` and `suggest`. A read-only reviewer can inspect the frozen observations. Give executable verification access through the same controlled interface for both arms if needed. Imported product cases supply recorded outputs from the product's real entry point.
3. Save the first object before presenting the author's defense. Resume the **same session** for its final object. Use the same defense text in both arms. The following transcript uses example paths for the operator's two response files. Substitute the actual runtime session and model identifiers.

```sh
python3 "$lab" submit "$work_root/run" t001 guardian pre --session G1 --model "$model_id" --response "$work_root/g1-first.json"
python3 "$lab" defense "$work_root/run" t001 guardian --session G1
python3 "$lab" submit "$work_root/run" t001 guardian post --session G1 --model "$model_id" --response "$work_root/g1-final.json"
python3 "$lab" score "$work_root/run"
python3 "$lab" audit-packet "$work_root/run" t001 --out "$work_root/handoff"
```

Repeat for `baseline` with its own session and responses. Optional `--tokens`, `--seconds` and `--human-minutes` are **incremental** per submission. Omit a missing measurement. A duplicate submission fails. A changed packet, new session or different model cannot replace the locked initial response. If the code or effective sources change, prepare a new run. An audit export contains the reviewed material, available decision records and the Inspector assignment, without reference labels. Give the Inspector just that folder.

The packets keep reference labels, the defense and sibling results outside the working directory. The fixture suite is public and the directories are ordinary files. For a real blind comparison, supply only the exported directory through an isolated runner, use unpublished cases and record the exact tool permissions. An operator who can rewrite both the plan and its digest is trusted. For a consequential comparison, preregister the plan hash and rubric with an independent custodian.

## Bring a real PR and its implementing Lead

Create an operator manifest outside the product checkout. `repo` and `observations` resolve relative to the manifest. Use a reviewed ancestor base and candidate commit. Capture each accepted source as the tracked file at the base revision. Cite the human acceptance event and confirm it applies to that exact revision. The importer reads Git blobs and the diff. The operator supplies the outcome capture from the reviewed head.

```json
{
  "label_provenance": "Record the independent labelers and adjudication reference here",
  "cases": [{
    "id": "change-17", "family": "explicit-finish", "split": "evaluation",
    "repo": "../product", "base_sha": "<full base commit>", "code_sha": "<full candidate commit>",
    "acceptance_ref": "<verified approval bound to the base corpus>",
    "sources": ["CANON.md"], "missing_sources": [], "prior_consult": [],
    "observations": "change-17-outputs.json", "task": "Review reading progress on opening.",
    "defense": "The author supplies their recorded explanation here."
  }],
  "labels": {
    "change-17": {
      "gate": "NO-GO", "routes": [], "advisory": false,
      "blocks": [{"clause": "R-01", "action": "open", "field": "marks_complete", "value": true}]
    }
  }
}
```

For the example, `change-17-outputs.json` includes `{"open":{"marks_complete":true}}`. Replace illustrative clauses, values and references with independently verified product data. Include relevant adjacent entry points. Reviewers see `prior_consult`, so record relevant history and state what the arms share. Keep the rubric and human labels with the operator.

```sh
python3 "$lab" prepare "$work_root/product-run" --manifest /path/to/manifest.json --split evaluation
python3 "$lab" bind-author "$work_root/product-run" t001 --session "$author_session" --head "$candidate_sha" --evidence "$authorship_reference"
```

Bind authorship **before the first response**. The operator verifies the transcript or execution record that connects the implementing Lead session to the actual candidate head. Resume that session for the `lead-self` arm with the same additional-review budget. The database checks the registered session and SHA. It cannot authenticate the person or prove authorship on its own. A freshly isolated code reviewer belongs in `baseline`. The supplied fixture diffs have no agent author session. Keep `lead-self` empty for them.

## What to read in the results

| Field | Interpretation |
|---|---|
| `coverage` and `exact` | Number adjudicated out of those planned, then agreement on gate, open routes, advisory presence and reference witnesses among submitted observations. Free-text reasoning needs a human read. |
| `precision` and `recall` | A detection requires the registered clause and matching observable witness. A correctly guessed `NO-GO` with evidence for another finding is counted separately. A valid alternative witness absent from the rubric needs blinded human adjudication. |
| `false_block` and `hold` | False blocks are predicted `NO-GO` on reference `GO` cases. HOLD is reported across all observed cases. Ambiguous or missing-context cases have their own reference labels. |
| `shared_miss` | Among violating cases where the genuine Lead initially issued `GO`, count matching Guardian `GO` judgments before and after defense. Zero denominators or incomplete pairing produce `null`. |
| `dialogue` and `usage` | Inspect paired changes with the defense and evidence. A change in output does not identify its cause. Sum usage across both stages, keep missing measurements unknown and flag observed budget overruns. |

Separate calibration and evaluation **by change family**. The built-in set has five calibration and six evaluation cases. Using `--repeats` gives separate sessions, not independent product families. For an effectiveness study, report results by family, organic versus injected failures, uncertainty and intervention cost. Estimate uncertainty on paired families, keep missing pairs visible and preregister decision thresholds. Judge whether changed decisions followed new evidence, corrected interpretation or unsupported pressure.

## Skills, roles and the local hook

| Component | Responsibility |
|---|---|
| [cdd-init](../../skills/cdd-init/SKILL.md) | Draft project files for a human to review and ratify. |
| [Lead](roles/cdd-lead.md) | Implement in the product checkout, record checks and provide evidence. Its profile can also brief the main authoring agent. |
| [Guardian](roles/cdd-guardian.md) and [cdd-guardian](../../skills/cdd-guardian/SKILL.md) | Review in a separate context, carry relevant history through consultation and dialogue, and preserve each open question. |
| [Inspector](roles/cdd-inspector.md) and [cdd-inspect](../../skills/cdd-inspect/SKILL.md) | Inspect a supplied decision trail. Report scope, continuity and ownership gaps to the operator. |
| [Git hook](hooks/pre-commit) | Runs the repository tests and fixture check in a contributor checkout. Run it directly or opt in with `git -c core.hooksPath=experiments/phase0/hooks commit …` for one commit. It checks the working tree. |
| [CI recipe](../../.github/workflows/phase0-lab.yml) | Runs the mechanical checks at PR time. It does not issue a product verdict. |

Claude Code can load a single local plugin with the three roles and portable skills:

```sh
python3 experiments/phase0/lab.py package-plugin --out "$work_root/cdd-plugin"
claude --plugin-dir "$work_root/cdd-plugin"
```

The plugin builds from the repository's copies. Load it for project work. For a controlled comparison, use the arm-specific export instead, so the baseline does not inherit the Guardian skill. The Guardian export includes project skill paths for Claude Code and Codex. Its `.claude/agents` file configures a Claude Code subagent. In another runner, use `ASSIGNMENT.md` in a separate session and configure tool permissions there. The portable skill files alone do not enforce an access boundary. [Claude Code plugin reference](https://code.claude.com/docs/en/plugins-reference) · [Claude Code subagents](https://code.claude.com/docs/en/sub-agents) · [Agent Skills specification](https://agentskills.io/specification)

## Rolling the pilot into an ADLC

Start with a human-approved statement of what user behavior should survive. The Lead turns it into an acceptance example and implements a small vertical change. Apply mechanical checks, capture the public outcome and have the Guardian record its assessment. Send existing-rule ambiguity to Council, a genuinely new norm to the human Master, and missing sources to an owner who can provide them. A valid BLOCK can coexist with open work. The product owner tracks unresolved items and their age. Ordinary engineering review, release and rollback follow the project's own controls. Feed real customer-facing deviations back into the case set.

An individual diff measures an evaluator. To test the product claim, trace a sequence of 100–500 real changes and repeat on a second product with a different identity. Track human review minutes, oldest open item, false blocks, idle HOLD time and soft advisory accumulation. Reduce the semantic gate's scope if its incremental benefit falls below the approved cost. [CDD experimental protocol](../../cdd.md#11-experimental-protocol)
