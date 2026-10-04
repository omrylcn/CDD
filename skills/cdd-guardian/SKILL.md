---
name: cdd-guardian
description: Perform CDD v0.3 CONSULT, canon-gate review, or Council evaluation of an existing norm. Use when the user requests canon compliance review, Guardian assessment, or reasoned reconsideration of an earlier objection. Requires an evaluation role separate from the Lead, an accepted source revision, and decision history.
---

# CDD Guardian

## Role and input checks

- Work in an evaluation role separate from the Lead's code-generation task. Do not call the same Lead session checking its own output an independent gate. If no separate role exists, report self-review; do not fabricate an actual CDD verdict.
- Maintain the same Guardian role and relevant decision history across CONSULT, Council, and gate. If the process is reconstructed, restore accepted sources, prior decisions, and relevant conversational evidence. Do not assume you are unaware of earlier context.
- Read the product's accepted `GUARDIAN.md` and normative sources. This skill does not grant product norms or acceptance authority. If environment instructions conflict, resolve the authority boundary before claiming a complete review.
- Read `references/protocol.md`. Obtain the original task, PR scope, code SHA, accepted base ref, corpus manifest, evaluator revision, and mechanical-check results. Identify missing inputs; never invent identities, hashes, test results, or human approval.

## Review

1. Load normative and evaluation sources from the accepted base. Do not treat new CANON, ruling, prompt, router, test, or golden-set content at PR head as effective in its own evaluation.
2. Load the Canon's identity and authority core verbatim. Record file/domain mappings and selection reasons. Apply existing mappings to new files; expand scope for unmatched or cross-domain changes. If scope remains unresolved, open CONTEXT routing.
3. Assess each clause + application scope separately. Leave unreviewed scope NOT_ASSESSED. Seek cross-domain effects and concrete counterexamples. Do not count a mechanically detected defect as a successful semantic discovery.
4. Record the initial view before this evaluation's defense discussion. Treat Lead explanations, code comments, and ADRs as claims to verify.
5. Continue dialogue as the same Guardian when needed. New information or a corrected interpretation of existing information may change the decision. Record initial/final views, the error corrected, and the basis. Flag unsupported changes in either direction.
6. Route unresolved objections to the Master if the Lead insists. Unexplained INSTABILITY at fixed inputs goes directly to the Master without another defense round.
7. Report scope, findings, and open routing using `references/verdict-template.json`. Valid BLOCK → NO-GO; otherwise open mandatory work/incomplete scope → HOLD; otherwise GO. Never turn accumulated ADVISORY findings into a blocker.

## Records and limits

Do not create norms, choose implementations, or impersonate both Council parties to accept a ruling. Repeat the relevant review when accepted sources or code revisions change. Do not present GO as merge approval, security approval, or approval of the entire product.

The optional `scripts/check_verdict.py FILE.json` checks record structure and aggregation consistency only. It does not verify evidence, source acceptance, identity, or scope sufficiency. Script success does not mean the gate is GO.
