---
name: cdd-init
description: Prepare CDD Phase 0 in a new or existing project. Use when the user requests Canon-Driven Development setup, starter CANON.md, GUARDIAN.md or AGENTS.md files, or adaptation of a CDD example to their product. Separate draft norms from human acceptance and preserve existing files.
---

# CDD initialization

1. Read the target project and its existing `AGENTS.md` instructions. Establish whether this is a new product or an existing one. Infer product identity from available code and the human's request; do not transfer fictional example rules into another product.
2. Read `references/bootstrap.md`. If product identity is incompletely specified, prepare a limited draft; do not turn unknowns into norms.
3. From the package directory, run `scripts/init_cdd.py --target TARGET --dry-run`. If conflicts exist, read the existing files and prepare a reconciliation proposal; do not bypass the script's no-overwrite behavior.
4. If no conflicts exist, run the same command without `--dry-run`. If necessary, use `--skip-agents` during initialization to preserve an existing `AGENTS.md`, then explicitly reconcile the required CDD instructions with it. This option does not establish role separation.
5. Clarify the DRAFT fields in `CANON.md` with the product owner. Do not count script output, a commit, or `ratified_by` text as Master approval. Do not mark it ACTIVE before acceptance; record the accepted content revision and a verifiable source of the human decision.
6. Separate Lead and Guardian evaluation roles using capabilities the environment actually supports. If role separation cannot be established, label a second reading by the same agent as self-review rather than a CDD gate.
7. For the first task, record the accepted base revision, original task, and code revision under review. Use the `cdd-guardian` package in the separate Guardian role. Maintain the same Guardian with relevant history across CONSULT, Council, and gate.
8. Report created files, open product decisions, and missing integrations. Prepare a first review example; do not imply that semantic correctness or branch protection has been established.

The script only creates a file scaffold. It does not run agents, accept norms, approve PRs, or configure CI enforcement.
