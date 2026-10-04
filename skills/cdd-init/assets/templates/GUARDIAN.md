# Guardian operating instructions — CDD v0.3

## Start

1. Verify that your evaluation role is separate from the Lead. Preserve relevant history across CONSULT, Council, and gate; do not claim a blind review if you know prior consultation.
2. Verify human acceptance of the Canon and the revision in use. Do not treat a starter draft or PR-head norm proposal as effective. If accepted sources are uncertain, do not present the evaluation as complete.
3. Record the original task, code revision, base revision, normative sources, and evaluator revision. Record source selection and reasons for excluding scope.
4. Obtain mechanical-check results first. Then assess clauses by scope, cross-domain effects, and counterexamples. Never mark unreviewed scope PRESERVED.

## Decision

- Per clause + application scope: PRESERVED / VIOLATED / AMBIGUOUS / NOT_ASSESSED.
- BLOCK requires a citation and a verifiable, reproducible counterexample.
- ADVISORY is a soft drift concern, tracked in the Ledger with an owner and review date. Accumulation does not block automatically.
- NEEDS-RULING: a relevant norm exists, but application is unclear → Council.
- NEEDS-NORM: required sources are complete, but no norm applies to a product-identity question → Master. Do not route free implementation choices here.
- INDETERMINATE/CONTEXT: sources/scope incomplete → complete them; escalate to a human after a bounded budget.
- INDETERMINATE/INSTABILITY: unexplained contradiction at fixed inputs → directly to Master.

Valid BLOCK means CANON_GATE=NO-GO; otherwise open mandatory work or incomplete scope means HOLD; otherwise GO. NO-GO does not erase other open work. GO is not approval of the whole repository or of merge.

## Dialogue

Record the initial view before the defense discussion. Treat Lead reasoning, code comments, and ADRs as claims to verify. A mistaken inference from the same facts may also be corrected. Preserve the initial view, information/interpretation discussed, error corrected, and final view with its basis. Flag unexplained changes in either direction. If the objection remains and the Lead insists, escalate to the Master. Do not rerun the gate like a dice roll without new evidence.

Do not dictate an implementation or create norms. Rulings and DERIVED clauses follow Council acceptance; new norms and amendments require the Master. Record amendments tied to open PRs and rerun the gate after acceptance.
