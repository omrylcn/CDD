# Working in the CDD repository

This repository contains the CDD method, starter templates, and examples. The fictional coordination application's canon clauses are not product rules for this repository.

- English is the primary project language. This branch carries the v0.4 draft in `cdd.md` and its Turkish version in `cdd.tr.md`. Keep both aligned when the protocol changes. README, guides, skills, templates, examples, and tool output stay in English.
- Keep role and body identifiers in English in both specifications: Master, Lead, Guardian, Inspector, Council. Translate explanations, not these identifiers. Guardian reviews canon compliance; Inspector audits the process; Council interprets existing norms.
- Preserve the original narrative and section numbering. When changing the protocol, update the relevant skills, templates, examples, and diagrams together.
- The same Guardian role carries relevant decision history through CONSULT, Council, and gate. Lead reasoning is a claim to verify, not a norm or independent approval.
- Distinguish `CANON_GATE` from merge approval. Valid BLOCK → NO-GO; otherwise open mandatory work or incomplete scope → HOLD; otherwise GO. Accumulated ADVISORY findings never block automatically.
- Do not fabricate example approvals as actual Master approval. Scaffolds are DRAFT; real acceptance is a separate event bound to human identity and content revision.
- Skills under `skills/` are portable packages. Do not install them into the user's personal skill directory automatically. Target-project instructions live in `skills/cdd-init/assets/templates/AGENTS.md`.
- The initializer must never silently overwrite existing files; conflicts must stop it before any writes.
- Run `python3 -m unittest discover -s tests -v`. Check relative document links and Mermaid diagrams as relevant to the change.
- Do not merge or release unless the user requests it. Prepare changes on a branch with a reviewable PR.
