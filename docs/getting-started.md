# Starting CDD in a project

This guide establishes Phase 0: a short Canon, a separate Guardian evaluation role, and a decision record. The script prepares files; it does not configure agent orchestration, human approval, or CI enforcement.

## 1. Generate draft files

From the CDD repository root, explicitly name the target product directory:

```bash
python3 skills/cdd-init/scripts/init_cdd.py --target ../my-product --dry-run
python3 skills/cdd-init/scripts/init_cdd.py --target ../my-product
```

Outputs: `AGENTS.md`, `CANON.md`, `GUARDIAN.md`, `RULINGS.md`, and `CDD_LOG.md`. Existing different content or symlinks stop the operation before any writes. Running again with identical templates changes nothing. Use `--skip-agents` to preserve an existing AGENTS file while preparing the other missing files; manually reconcile the CDD instructions with the existing AGENTS instructions afterward.

## 2. Write and accept product identity

Fill in `CANON.md` for the actual product. Do not automatically copy the fictional coordination application's principles. Keep the document DRAFT until the human product owner accepts the principles and authority clause.

In `CDD_LOG.md`, link the accepted norm text's revision or hash to a verifiable source of the human decision. Writing `ratified_by: Master` or creating a commit does not prove acceptance. The trusted source commit established after acceptance becomes the base for later reviews. Keep the acceptance record in another commit to avoid a circular file attempting to contain its own commit hash.

## 3. Connect the roles

The Lead produces code. Give the separate Guardian role the accepted `GUARDIAN.md`, Canon, relevant ACTIVE rulings, original task, and diff. Both roles may use the same model; that does not establish independent errors.

Maintain the same Guardian role and relevant history across CONSULT, Council, and gate. Do not open a fresh Guardian instance to erase history while the Lead contests an objection. If the process restarts, restore the necessary decision record and source revisions. If the environment cannot support a separate evaluation role, use the workflow as self-review; a CDD gate has not been established.

Portable packages: [cdd-init](../skills/cdd-init/SKILL.md) and [cdd-guardian](../skills/cdd-guardian/SKILL.md). Place the **entire package** in the target agent's supported skill directory, or explicitly load the SKILL.md instructions. This repository's `skills/` directory does not install anything automatically. Example requests: “Use $cdd-init to prepare Phase 0 drafts for this product”; in the separate Guardian role, “Use $cdd-guardian to review this diff.”

## 4. Prepare the first review package

Use full commit IDs. `CDD_BASE_SHA` is the human-accepted source commit, not automatically the current HEAD. Run these commands in the target product repository:

```bash
CDD_BASE_SHA='<full-accepted-commit-sha>'
CDD_HEAD_SHA='<full-commit-sha-to-review>'
git show "$CDD_BASE_SHA:CANON.md"
git show "$CDD_BASE_SHA:GUARDIAN.md"
git show "$CDD_BASE_SHA:RULINGS.md"
git diff --name-status "$CDD_BASE_SHA" "$CDD_HEAD_SHA"
git diff "$CDD_BASE_SHA" "$CDD_HEAD_SHA"
```

Inspect more files read-only as needed. Distinguish code changes, norm proposals, and evaluation-apparatus changes; do not automatically activate rules from the PR head. In Phase 0, loading the entire small corpus may suffice. Include the source manifest and selection reasons, excluded scope, original task, mechanical-check results, and model/prompt revision. Mark missing inputs explicitly.

## 5. Initial assessment, dialogue, and decision

The Guardian records its initial view first. If the Lead supplies a counterexample or explanation, the same Guardian evaluates it; retain the basis of the initial and final views. Unresolved objections go to the Master if the Lead insists. INSTABILITY does not open another persuasion round.

| Result | Action |
|---|---|
| GO | Canon review complete; continue with other tests/reviews |
| NO-GO | Correct or resolve the reasoned objection; retain other open work |
| HOLD | Complete sources, scope, or the authorized decision; do not rerun merely to seek GO |

The [verdict template](../skills/cdd-guardian/references/verdict-template.json) starts on HOLD. Do not pass an example record off as an actual review. From the CDD repository root, check the JSON contract with:

```bash
python3 skills/cdd-guardian/scripts/check_verdict.py examples/coordination/verdicts/block.json
```

Exit code zero means **the record is structurally consistent**; this example's gate is NO-GO. Do not use the command alone as a GitHub merge check: it does not verify semantic correctness, identity, or source acceptance.

## 6. Work through the example, then connect automation

The [coordination example](../examples/coordination/README.md) covers explicit violations, soft drift, norm gaps, missing sources, and reasoned correction. These are synthetic teaching cases, not real-world results.

When adding a real PR gate, bind its output to full code/base/corpus/evaluator revisions. Verify who may produce trusted decisions and who holds human acceptance authority. Agent-written JSON saying GO is not enforcement. A new commit or accepted source change invalidates the old verdict. This starter package does not automatically alter platform protections.
