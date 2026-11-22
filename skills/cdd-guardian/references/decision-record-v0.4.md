# v0.4 decision record · draft

A Guardian supplies the verdict. A trusted operator supplies a separate context for the same task, candidate commit, accepted base, corpus and evaluator. In a small project the operator can prepare this by hand. Retrieve or verify it independently of the change under review. The Guardian can propose additional scope and observations. Freeze the updated context before issuing the corresponding verdict.

## Check a record

```sh
python3 skills/cdd-guardian/scripts/check_verdict.py --hash-context operator.json
python3 skills/cdd-guardian/scripts/check_verdict.py verdict.json --context operator.json --require-review
```

`--hash-context` computes SHA-256 over UTF-8 JSON with sorted object keys, compact separators, unescaped non-ASCII characters and the original array order. Put this value in `inputs.context_sha256`. Preserve both inputs after the review. A digest detects mismatched content. Obtain the authoritative copy, including the evaluator, from outside the candidate's write boundary. For example, an operator can export it from a protected revision and an identity-verified decision ledger. Independently verify the actual norm bytes and observations. An untrusted author can compute a digest too.

`--require-review` accepts only a v0.4 `record_kind=review` verdict paired with `context_kind=review`. Exit zero confirms record consistency. Read `canon_gate` to determine the outcome. For a teaching run, use `example` in both documents and omit `--require-review`. The starter template remains on HOLD.

## What the operator freezes

| Context field | Contents |
|---|---|
| `inputs` | The same `code_sha`, `base_sha`, `corpus_hash`, `task_ref` and `evaluator` that identify the review. The corpus hash is a lowercase SHA-256 of the product's frozen source manifest. |
| `expected_scope` | Rows with a unique `scope` and a list of required `clauses`. Use distinct rows for independently affected paths. A surface without an applicable clause can start with an empty list while a product decision is open. |
| `evidence` | Unique `ref`, the `scope` and the captured `observation`. Cite an immutable test run, transcript or source snapshot as appropriate. The trusted collector records what it actually observed. |
| `human_masters` | Stable principal IDs verified as authorized human Masters for the relevant decision. A display name or a self-declared role does not authenticate this list. |
| `norm_requests` | Each expected request has a unique `request_id`, its `scope`, `follow_up_owner`, `norm_revision` and `decision`. Use explicit null for a pending decision. The revision can be null until proposed text exists. The registry preserves the tracking assignment after closure. |

Source selection still records which norms were loaded. The expected surfaces describe which behavior needs an assessment. If the inventory is unavailable, use an empty list with open CONTEXT routing. A second, supported violation can still determine NO-GO.

## How the Guardian accounts for a surface

- Each expected clause gets a `clauses` row with the same `scope` and `required: true`. A PRESERVED or VIOLATED row cites an `evidence_ref` registered for that surface. A BLOCK also needs the original citation and reproducible counterexample. Keep incomplete or ambiguous required assessments visible.
- For an entirely excluded surface, supply `scope.exclusions` with `scope`, a concrete `reason` and a `basis_ref`. The corresponding independent inventory row must explicitly authorize that reference as `exclusion_ref`. A surface cannot be assessed and excluded simultaneously. For a partial exclusion, identify the two behaviors separately.
- A surface with an empty clause list needs an assessment, an authorized exclusion, or an open route on that surface. For instance, a new shared shelf may need an identity decision from the Master. Free implementation choices can use a justified exclusion. A documented change whose every surface is validly excluded may receive GO.
- Additional assessments can extend the frozen minimum. Missing an expected row invalidates the submitted record. Recording the required row as NOT_ASSESSED leaves an honest HOLD or a separately supported NO-GO. The Inspector can inspect the actual diff for effects missing from the inventory.

## Who follows up and who decides

Every open route records `kind`, `scope`, `reason`, `follow_up_owner` and `decision_authority`. NEEDS-NORM also needs a stable `request_id`. NEEDS-RULING retains its `cite`. Open routes carry no approvals.

| Open route | Decision authority |
|---|---|
| NEEDS-NORM | Master |
| NEEDS-RULING | Council |
| INSTABILITY | Master |
| CONTEXT | `null`. The follow-up owner obtains the missing inputs. |

A newly discovered norm question can open immediately. Carry it into the independent request register before the next review so deletion from a later candidate cannot make it disappear. For a registered pending question, the ID, scope and assigned follow-up owner stay in routing even if another finding determines NO-GO. A Lead may be its follow-up owner. Record a reassignment in the register and bind the next record to the updated context.

The human decision is stored independently from that route. Its `outcome` is `ACCEPTED` or `DECLINED`. It identifies the stable `principal_id`, the SHA-256 of the exact proposed text bytes as `norm_revision`, and an identity-bound `decision_ref`. The operator checks the event against the authorized human and records which accepted `base_sha` and `corpus_hash` make that disposition applicable to this review. These last two values describe applicability. The original human event may be older than the reviewed base.

Once decided, the fresh verdict includes the matching fields plus `request_id` in `norm_decisions`. Keep the earlier verdict on its original context. An acceptance alone does not decide the candidate's gate. Assess the behavior again on the accepted sources. A declined proposal provides no authority to implement it. An operator can rebind an existing event only after verifying that its text, authority and applicability still hold.

## Migrating from v0.3

Historical `0.3` records work with the original single-file command. Preserve them as history. For a current v0.4 decision, obtain the independent inventory and observations, recover the evidence for any applicable human decisions, and perform a fresh assessment. A renamed `owner` field or a copied GO cannot supply the missing evidence. Existing initialized project files can be reconciled manually with the new templates. The initializer retains its conflict checks.

The runnable reading-desk example prints three valid outcomes and three rejected records. It can retain its complete JSON inputs using `python3 experiments/phase0/record_demo.py --out /path/to/new/folder` from the CDD repository. All identities and acceptance events in that example are explicitly simulated.
