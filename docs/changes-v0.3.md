# v0.2 → v0.3 change summary

This revision builds on the collaboratively prepared Turkish v0.2 draft. The repository previously contained v0.1, so the original v0.3 PR showed a v0.1 → v0.3 diff. This table describes the v0.2 → v0.3 changes settled in the final review. The subsequent language update makes English primary and retains the Turkish specification as `cdd.tr.md`; it does not introduce a new protocol version.

| Section | Change | Result |
|---|---|---|
| §0.1 | Reading path, role table, daily loop, short glossary | Readers see the main workflow before detailed rules |
| §2 and §2.3 | Layer and ruling-lifecycle tables | Compare authority and effective status directly |
| §3.1 and §8 | Three-part limit moved forward | Separates constraints on agents from the Master's responsibility |
| §3.1, §4 | Open-PR amendment record and separate acceptance | Links proposals even before NO-GO; new norms cannot carry over old verdicts |
| §3.1.1, §11 | Master work queue; open count and age by class | Distinguishes producing records from doing reviews |
| §3.3, §3.4, §3.6 | Separates authority from error independence; softens categorical correlation claims | Preserves the same Guardian and reasoned dialogue while exposing shared blind spots |
| §6, §10 | Scope-selection record and unmatched / cross-domain routes | New files may match existing rules; unresolved scope cannot receive GO |
| §11 | Shared misses before/after dialogue; source vs. interpretation errors | Separates GO on violations, HOLD, and NO-GO with incorrect reasoning |
| §10 | Staying small and withdrawing layers | Records where protection continues or which risk is accepted |
| §8, Appendix A | Historical examples moved to appendix; broad institutional-purpose claim removed | Keeps the main flow lighter; analogy is not evidence of correctness |
| §9.7 | Corrected starter-file count | Consistently lists CANON, GUARDIAN, RULINGS, and gate instructions |

## Six diagrams

1. Daily development loop (§0.1).
2. Acceptance of an amendment tied to an open PR, followed by reevaluation (§3.1).
3. Reasoned objection with the same Guardian (§3.3).
4. Boundary between accepted sources and PR head (§4.2).
5. Aggregation into GO / NO-GO / HOLD (§6).
6. Missing sources, a norm gap, and interpretive ambiguity (§6).

Markdown contains the Mermaid sources. `docs/cdd-v0.3.html` presents the same English text with embedded SVG diagrams, requiring no external service or JavaScript. Tables support comparisons, diagrams show procedures, and code blocks retain data examples.

## Starter package

- Root `AGENTS.md` for repository contributors; a separate target-project AGENTS template.
- `skills/cdd-init`: a skill and initializer that produce DRAFT files and refuse conflicting writes.
- `skills/cdd-guardian`: separate evaluation role, same Guardian history, source boundary, dialogue, and verdict contract.
- `docs/getting-started.md`: from first norm acceptance to first review.
- `examples/coordination`: six synthetic gate records and a reasoned-correction scenario.
- `tests/test_starter.py`: file preservation, repeat runs, symlink boundaries, and verdict aggregation.

Script and record checks do not measure a semantic judge's performance. Identity-bound human approval, agent orchestration, and real PR enforcement require separate setup. The current English and Turkish specifications both describe v0.3; the obsolete v0.1 English file is removed from the current tree and remains in Git history.
