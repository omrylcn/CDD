# Canon-Driven Development

> As code gets cheaper, the real problem stops being writing code; it becomes keeping the system the same thing across thousands of small changes.

CDD is a governance proposal for preserving a product's identity across small changes in agentic development. The Lead implements, the Guardian evaluates against the Canon, and the Inspector reports on the process; the human Master establishes norms. The same Guardian continues reasoned dialogue. If an objection remains unresolved and the Lead insists, the Master decides.

**v0.4 draft.** The draft binds coverage to observed behavior and separates tracking a norm request from deciding it. The published v0.3 remains available in the [archived browser edition](docs/cdd-v0.3.html).

| What you need | Start here |
|---|---|
| Understand the method and workflows | [Full specification with six Mermaid diagrams](cdd.md) |
| Read the archived illustrated v0.3 edition | [Single-file HTML](docs/cdd-v0.3.html) — download and open in a browser |
| Try the v0.4 decision record | [Rules and migration](skills/cdd-guardian/references/decision-record-v0.4.md) · [Runnable example](experiments/phase0/README.md#exercise-the-v04-decision-record) |
| Start Phase 0 in a project | [Setup guide](docs/getting-started.md) |
| Portable skill packages | [cdd-init](skills/cdd-init/SKILL.md), [cdd-guardian](skills/cdd-guardian/SKILL.md), [cdd-inspect](skills/cdd-inspect/SKILL.md) |
| Run a shadow review or compare evaluators | [Phase 0 experiment and agent profiles](experiments/phase0/README.md) |
| Explore the first gate examples | [Coordination example](examples/coordination/README.md) |
| Review v0.2 → v0.3 changes | [Change summary](docs/changes-v0.3.md) |
| Read the Turkish specification | [Türkçe — cdd.tr.md](cdd.tr.md) |

## Quick start

Python 3.10+ is sufficient; the starter tools have no external dependencies.

```bash
python3 skills/cdd-init/scripts/init_cdd.py --target ../my-product --dry-run
python3 skills/cdd-init/scripts/init_cdd.py --target ../my-product
```

The script creates DRAFT files and never overwrites existing content. Human norm acceptance, a separate Guardian role, and platform permissions/CI must be set up separately. Install skill packages in the target agent separately; this repository does not automatically install them into a personal skill directory.

## Checks

```bash
python3 -m unittest discover -s tests -v
python3 skills/cdd-guardian/scripts/check_verdict.py examples/coordination/verdicts/block.json
```

The second command checks the record contract; the example has CANON_GATE=NO-GO. A successful script exit is not merge approval. Synthetic examples are neither model-performance measurements nor real product results.
