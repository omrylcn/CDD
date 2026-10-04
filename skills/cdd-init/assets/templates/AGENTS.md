# Working with CDD in this project

First check the status of `CANON.md` and actual human acceptance. Do not enforce DRAFT norms as binding canon; clarify principles with the product owner. Read `GUARDIAN.md` for operating instructions and `RULINGS.md` for interpretation history.

- The Lead implements; a separate Guardian role reviews canon compliance. Do not present an agent rereading its own code as an independent gate.
- Preserve the same Guardian role and relevant decision history across CONSULT, Council, and gate. Record the initial assessment before the current defense discussion.
- Separate the accepted base ref from the PR head under review. CANON, GUARDIAN, ACTIVE ruling, router, and evaluation-apparatus changes do not automatically take effect in their own PR.
- Bind the original task, scope, source revisions, and code revision to the review. Treat reasoning as claims to verify.
- After NO-GO, correct the change or discuss the objection with the same Guardian. Unresolved objections with continued Lead insistence go to the Master. INSTABILITY goes directly to a human.
- GO does not replace other tests or code review. ADVISORY counts never automatically produce HOLD/BLOCK.
- Separate norm proposals from acceptance. Do not impersonate human approval or treat a filled metadata field as approval.

These are starter instructions; they do not configure access rights, branch protection, or agent orchestration. Apply them together with existing project instructions.
