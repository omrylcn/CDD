# Reading the first gate together

This is a teaching exercise. The verdicts below are **synthetic examples** of expected behavior, not recorded model runs. Their assumed norms are in [CANON.md](CANON.md); they are not accepted norms for a real product.

## Rehearse setup

From the CDD repository root, generate starter files in a temporary directory:

```bash
python3 skills/cdd-init/scripts/init_cdd.py --target /tmp/cdd-demo --dry-run
python3 skills/cdd-init/scripts/init_cdd.py --target /tmp/cdd-demo
```

Fill in the DRAFT Canon's product identity. In real use, it cannot become a gate source without human acceptance. For this exercise, read the cases assuming the illustrative norms in this folder. Compare your conclusions with the expected records.

## Cases

| Case | Change / information | Expected route | Record |
|---|---|---|---|
| Explicit violation | Legacy fallback uses the client's `role` when the server role is absent | C-04 citation + concrete counterexample; NO-GO | [block.json](verdicts/block.json) |
| Soft drift | Three information-only cards added to Everyday; no administrative action | ADVISORY and follow-up; GO if no other open work | [advisory.json](verdicts/advisory.json) |
| Norm gap | Product decision asks how many days to retain old activity records; example corpus is silent | NEEDS-NORM; HOLD | [needs-norm.json](verdicts/needs-norm.json) |
| Missing sources | Required scope for a new integration cannot be established | CONTEXT; HOLD if no other BLOCK | [context.json](verdicts/context.json) |
| Interpretive ambiguity | An Everyday link only opens Operator without changing roles; its boundary is disputed | C-09 citation, NEEDS-RULING; HOLD | [needs-ruling.json](verdicts/needs-ruling.json) |
| Model instability | Unexplained contradictory judgments with unchanged sources, task, and code | INSTABILITY; Master; HOLD | [instability.json](verdicts/instability.json) |

### Counterexample to the explicit violation

```python
# Proposed legacy behavior: a synthetic norm-violating example.
role = server_session.role or request.json.get("role")
```

If the server role is absent and the client supplies `role=admin`, client data enters the authority decision. Adding a comment saying “safe for migration” does not change that behavior. If existing tests catch it, mechanical checks stop it. Otherwise, convert the verified counterexample into a persistent test.

### Reasoned correction with the same Guardian

The Guardian initially reads a button as changing roles from Everyday and records a C-12 objection. The Lead shows that the code path only navigates to Operator. The Guardian verifies the action trace, recognizes that administration is not happening in Everyday, and withdraws this objection. Record both views, the code path examined, and the misreading. If interpretation of the link under C-09 remains unclear, NEEDS-RULING remains open; removing one objection does not automatically yield GO. GO is possible when all required scope is complete and other open work is resolved.

“We need to ship” does not serve the same function. If the actual C-04 violation remains, NO-GO remains. If the Lead insists, the Master decides; a norm change is separately accepted and the code is reviewed against the new norm revision.

### Check your reasoning

Do not automatically mark a new file unmatched if an existing path rule covers it. Do not assume scope is complete merely because a path matches when an existing file's change affects another domain. Do not pass a PR using its own proposed rules from head. Do not label a norm unavailable because sources are missing as NEEDS-NORM.

From the repository root, check record format with:

```bash
python3 skills/cdd-guardian/scripts/check_verdict.py examples/coordination/verdicts/block.json
python3 -m unittest discover -s tests -v
```

These checks test scripts and the record contract. They do not establish that CDD outperforms human review or that a model resolves the cases correctly.
