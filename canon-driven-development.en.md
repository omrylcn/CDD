# Canon-Driven Development

### A human–agent governance proposal for preserving identity in agentic software development

*v0.1 — initial proposal*

> As code gets cheaper, the real problem stops being writing code; it becomes keeping the system **the same thing** across thousands of small changes.

---

## 0. One paragraph

CDD keeps a software system's **identity** — what it is, what it is not, how it behaves — outside the code, in a short, verbatim text: the **Canon**. **Sub-books** derived from the Canon and **Rulings** issued for individual cases form the second and third layers. There are four roles: the **Lead** agent that produces code; the **Guardian** agent whose only loyalty is to the Canon and who holds veto power only; the **Inspector** agent that audits the process and only writes reports; and the human **Master** — the owner and author of the Canon, the final authority on what the Canon means and when it changes. The Lead builds, the Guardian guards, the Inspector audits; none of them can create Canon in the Master's place. The core of the proposal is not the canon file but the separation of powers: **the builder cannot be its own referee.**

---

## 1. Context and proposal

This proposal does not claim to have discovered something new; it builds an authority topology on top of several existing ideas.

**What we build on:**

- *Architectural fitness functions* — reducing architecture to rules that can be asserted in CI.
- *ADRs* — recording decisions together with their rationale.
- *DDD ubiquitous language* — a system not contradicting its own concepts.
- *Spec-Kit constitution* — keeping the project's governing principles in a separate file and checking compliance during spec/plan/implement.
- *Constitutional Spec-Driven Development* (Marri, 2026) — embedding non-negotiable principles into the spec layer; security-focused.
- *Specification Governance Reference Model* (Alenezi, 2026) — placing the stochastic generator inside a deterministic validation boundary.

The common pattern is a single pipeline: `constitution → generation → compliance`. Compliance is mostly done either by mechanical rules or by the generating agent itself.

**The gap we target** is twofold:

1. Fitness functions had to be mechanical. "Does this screen lead the user to a wrong mental model?" could not be mechanized. LLMs have made the **semantic fitness function** cheap — but if you ask the generating agent, builder bias determines the answer.
2. *Who interprets* the constitution is undefined in most approaches. If interpretive authority is undefined, either the builder referees itself or every interpretation falls back to the human.

**What we propose:** give the authority to interpret, apply, and audit the canon to separate agents; fix the owner of interpretive authority as a human; and specify, in an explicit map, which authority passes to whom under which circumstances.

The protected invariant is a single sentence: **no agent may both create a norm, apply it, and approve its own application.** "The builder cannot be its own referee" is the most common instance; the Guardian's inability to create norms and the Inspector's lack of authority are other faces of the same invariant.

---

## 2. Three layers

```
CANON             short · verbatim · rarely changes · enters every context
  └─ SUB-BOOKS       per domain · detailed · with isnad · loaded on demand
       └─ RULINGS      per case · chronological · can be promoted · can expire
```

Authority flows top-down: **canon > sub-book > ruling, always.** A lower layer cannot override an upper one by being more specific or more recent. Promotion flows bottom-up: recurring rulings rise into sub-books; rarely, sub-book clauses rise into the canon.

### 2.1 Canon

The Canon is the product's identity: what it is, what it is not, how it treats the user, which side it takes in which trade-off, and what it never does. It is a one-page text of numbered clauses, written by the product's owner. It does not list features; it bounds them. Sentences like "authority is decided on the server only" or "the everyday user surface and the administrator surface are separate" are canon — a developer can write clean, tested, working code that violates them, and the product stops being itself. The Canon exists precisely to catch that: the answer to "is it still the same product?", which tests cannot see. It enters every agent's context as-is and rarely changes.

The Canon is not a SPEC; it is the product's constitution. Its contents:

- What the product is / is not
- Immutable principles — short, numbered (`C-01`, `C-02` …)
- Which side is chosen in trade-offs
- Things never to be done
- **Who holds interpretive and amendment authority** (§4)
- **The sub-book map**: which book is loaded when which domain is touched
- **The apocrypha list**: documents flagged separately because they are likely to be mistaken for canon. Normativity is an allow-list: only files listed in the sub-book map are normative; everything not on the list is apocrypha by default

Canon rules:

1. **Never written detached from the product.** Its natural form is a `principles.md` grown from a seed: a principle is written, then built against. For a mature codebase the fallback is to extract the canon from the existing product — not to write it from imagination; otherwise code and canon become two separate sources of truth. Other documents in the repo are not canon and are marked as apocrypha.
2. **Principle lifecycle:** `DRAFT → Master ratification → CANON → implemented/verified`. A principle being implemented in code is evidence that it *was applied*, not that it *is right*. The normative step is the Master's ratification; in a one-person project that coincides with writing the principle — but for a principle proposed by the Lead it is a separate step.
3. **Enters verbatim, never summarized.** No agent takes the canon into its context as its own summary. Every paraphrase is a scribal error.
4. **Intra-canon conflicts are not resolved automatically.** If two clauses conflict, the gate closes; an explicit amendment is required. There is **no** "later clause overrides earlier" rule inside the canon — if there were, file order would become a constitutional amendment mechanism.
5. **Change leaves a trace.** Amendments carry metadata:
   ```
   C-17
     supersedes  : C-04
     ratified_by : Master
     date        : 2026-09-02
   C-04  [SUPERSEDED BY C-17]
   ```
   The old clause stays visible.
6. **Stays short.** One page is the target. Detail goes down into sub-books.

Example — every example in this document comes from the same fictional product: a coordination app in which members work under a single administrator, and the everyday-use surface (**Everyday**), the surface opened on request (**On-Demand**) and the administration surface (**Operator**) are kept separate:

> **C-04** — Authority cannot be derived from a name or from a client payload; it is server-derived only.
>
> **C-09** — Everyday, On-Demand and Operator are distinct interaction surfaces; they cannot be merged under a single generic dashboard.

### 2.2 Sub-books

Sub-books are longer, more concrete texts that unfold what a canon principle means in a particular domain. The Canon says "authority is server-derived"; the auth sub-book writes out what that means, one by one, for legacy compatibility paths, token refresh, admin bootstrap. They still speak "what / what not", never "how": they do not pick implementations, they draw boundaries. They are split by domain because the canon enters every context while sub-books are loaded only when the relevant domain is touched. Every clause has a known source: either the canon principle it derives from (DERIVED) or the Master's ratification and the principles it is consistent with (NEW NORM). A clause whose source cannot be shown either does not belong there or the canon has a gap. The Council writes them, the Master ratifies new norms; they sit below the canon.

Per domain (`auth`, `surfaces`, `data-model` …). Every clause carries an **isnad** — a derivation chain. And every clause is one of two kinds:

```
S-AUTH-12
  kind       : DERIVED
  canon      : C-04
  origin     : R-031 (stale client role=master case)
  date       : 2026-08-14
  clause     : Legacy compatibility paths do not accept client-originated role hints.
```

```
S-SURF-21
  kind             : NEW NORM
  source           : MD-014 (Master decision)
  ratified_by      : Master
  consistent_with  : C-09
  date             : 2026-08-30
  clause           : On-Demand sessions close after 30 minutes of inactivity.
```

| Kind | Definition | Who verifies | Who ratifies |
|---|---|---|---|
| **DERIVED** | An operational unfolding of an existing canon clause; derivable from the canon with a citation | Guardian | Council |
| **NEW NORM** | Introduces a new behavior the canon does not state | Guardian classifies as "new norm" | **Master** |

Without this distinction, sub-books are a privilege-escalation path: Lead + Guardian could produce binding rules the canon never stated. The Guardian makes the classification, and because it is a real risk that the Lead learns to "write new norms so they look derived", the Inspector samples DERIVED classifications. Every clause has provenance, but not every clause has a derivation from the canon: a NEW NORM's legitimacy is not derivation but the Master's explicit ratification — it still cannot contradict the canon, and `consistent_with` cites that.

The mechanical check of an isnad lives in CI: does the referenced clause exist, is it not SUPERSEDED, does the quoted text match the canon verbatim. For a NEW NORM: is `ratified_by` present, do the `consistent_with` clauses exist. This check does not verify derivation — blind re-derivation does that (§3.4) — but it instantly catches fabricated IDs and reliance on abrogated clauses. Vector similarity substitutes for none of this.

Precedence rules between sub-books are written down in advance:

- **lex superior** — the higher source wins; unconditionally
- **lex specialis** — the specific rule overrides the general one; **only at the same authority level** (sub-book vs sub-book, ruling vs ruling)
- **lex posterior** — at the same level, newer overrides older; invalid inside the canon

The isnad does two jobs: a clause that cannot be derived means either a gap in the canon or a clause that does not belong there (**gap detection**); when the concern that produced it disappears, the clause retires (**pruning**). Sub-books being a hundred times larger than the canon is not a problem; growing without isnad is.

### 2.3 Rulings

A ruling is the record of a single interpretive decision made where a relevant norm exists but how it applies to the case is unclear. The Lead wants to do something and asks "does this fit C-09?"; the clause exists but does not explicitly cover this case; someone has to interpret. That interpretation, with its reason, is written as one line in `RULINGS.md` so the same question is never interpreted from scratch again. A ruling does not make a new rule; it says what the existing clause says in this case. If no clause applies at all, that is not a ruling's job — it is a gap, and it goes to the Master. When rulings of the same kind accumulate, it is no longer a case but a rule, and it rises into a sub-book; when its conditions change, it expires. It is the lightest, fastest, most temporary layer.

A relevant norm exists but how it applies to the case is unclear — this is where interpretation happens. A ruling is a **Council decision**:

1. The Lead asks; the Guardian says "ambiguous", cites the ambiguous clause, and stops.
2. The Lead proposes an interpretation.
3. The Guardian checks the proposal against the cited clause: is it a reading of the clause, or something the clause does not say.
4. If it is a reading and consensus is reached → ruling, entered into `RULINGS.md`. It does not go to the Master; the Master sees the log and holds a **right of recall**.
5. If the Guardian says no and the Lead insists → Master.
6. Tie → status quo.

If the Guardian says "gap" — no clause applies — there is no ruling. The Council finds nothing to interpret and cannot create a norm. The case goes to the Master as NEEDS-NORM; the Master either adds it to a sub-book as a NEW NORM or, if it is identity-level, opens a canon amendment. The triad is: **the Guardian interprets and does not create norms. The Council interprets and does not create norms. Only the Master makes norms.**

What separates ambiguity from a gap is the citation: a claim of ambiguity must carry a clause number; if it cannot, it is a gap. This prevents the Guardian from presenting a gap as ambiguity to route the case to the Council instead of the Master; the Inspector samples NEEDS-RULING verdicts.

The name for this is **delegated interpretive authority**: the Master owns interpretive authority, delegates routine interpretation to the Council, and retains recall/abrogation power over every ruling. The Master is the ultimate authority; the Council is the first-instance interpreter. The delegation is not implicit — it is written in the canon's authority clause and can be narrowed by amendment. Interpretation stays light and fast; authority stays with the human.

Every ruling carries a lifecycle:

```
ACTIVE
  ├── PROMOTED     recurred, rose into a sub-book
  ├── SUPERSEDED   replaced by a newer ruling or clause
  ├── EXPIRED      its conditions changed
  └── ARCHIVED     stayed singular, kept for record
```

Only ACTIVE rulings are normative. An active ruling is temporary authority, not frozen precedent. So that lifecycle transitions do not become one-by-one bureaucracy, the AUDIT loop proposes PROMOTE/EXPIRE candidates in batches and the Council approves in batches. The log must not become a "this was decided that way before" machine — if the gate of ijtihad closes, the system freezes.

### 2.4 What and how — normative and non-normative

All three layers are **normative**: they say what the product is and is not. They do not say **how** to build it. "How" is the Lead's job; if a sub-book has no implementation detail, that is not "silence" — it is **freedom**. If a ruling were required for every implementation detail, the system would lock up.

The single test the Lead applies:

> **Would the answer to this question change what the product is?**

```
"Which middleware should derive authority?"                → no  → Lead decides
"Bulk assignment via queue or transaction?"                → no  → Lead decides
"Should Operators see a member list?"                      → yes → CONSULT (C-09)
"Should bulk role assignment exist at all?"                → yes → CONSULT
```

A normative clause **narrows the implementation space**; it does not pick an implementation. "No client-originated role hint may reach an authority decision path" is a norm; "use middleware X" is not. This is also why a compliance condition states only the target state: the method is deliberately left to the Lead.

"How" lives in a fourth, **non-normative** layer:

```
CANON > SUB-BOOK > ACTIVE RULING      normative — what / what not

TECHNICAL DOCUMENTS                   non-normative — how
  ADRs, design docs, code             owned by the Lead; apocrypha from the canon's view
                                      the Guardian reads them for context, never cites them as norm
```

Two failure modes:

- **Over-consulting** — the Lead brings every detail to CONSULT; a flood of NEEDS-RULING. Cheap; it reveals itself.
- **Under-consulting** — a normative decision passes disguised as a "technical choice"; nobody asks. This is the dangerous one. The Breaker pass and the audit catch it; the Inspector samples the decisions the Lead made on its own as "operational".

There is a drift in the opposite direction too: if a sub-book starts writing "how", it turns into a spec. If a sub-book clause picks an implementation, the Guardian flags it in the isnad check — norms derive from the canon, methods do not.

---

## 3. Roles

### 3.1 Master — human

Owner and author of the Canon. The final authority on what the Canon means and when it changes. Does not read every PR; makes **identity decisions**. Steps in for: canon-tier changes (even when the Council agrees), NEW NORM ratification, veto appeals, ties in the Council, audit and inspection results.

"Master" here is not the technical master node/branch; it is the person holding **constituent power** over the canon. The legal distinction maps exactly: the Master is the *constituent power* — puts the canon in place and ratifies amendments. The Lead, Guardian and Inspector are *constituted powers* — they operate with the authority the canon grants them, and none can create canon in the Master's place.

```
MASTER
  │  authors / interprets / amends
  ▼
CANON
  ├── Lead       → applies
  ├── Guardian   → guards
  └── Inspector  → audits the process
```

**The Master is above the Canon; the agents are not.** Implementation note: in some projects "master" is also a domain term (like the single-master invariant in the example product); in agent-facing files the role name and the domain term must be clearly separated.

**The Master can override the Guardian; the Master can only get past the Canon by changing it.** This is one of the most important sentences in the proposal and it separates two situations sharply:

```
If the Guardian misinterpreted
  → the Master overrides the verdict, the reason goes into RULINGS, the canon does not change.
  → the override feeds the Guardian's precision metric and the Inspector's sampling.

If the Guardian was right and the change really violates the canon
  → the Master cannot merge by ruling.
  → either the implementation changes, or the Master changes the canon by an explicit act of sovereignty.
```

Concretely:

```
Guardian:  C-04 violation → NO-GO

Master:
  "merge it"                                            ✗  silent override; the canon is breached
  "I'm changing C-04, open an amendment"                ✓  act of sovereignty; the canon changes
  "exception for this case, write it into the canon"    ✗  the canon does not accumulate cases
  "72-hour emergency exception, to the Ledger, lock the audit" ✓  debt; time-boxed, inspected
```

The Master can change the canon at any moment; the Master owns it. But silently **breaching** a rule in a single case instead of **changing** it reduces the canon to that day's decision — at that moment what binds the agents is no longer the canon but the Master's last decision, and the canon stops functioning. Sovereignty is exercised through explicit acts: amendment, abrogation. The owner changes the rule; the owner does not breach it.

An **emergency exception** is *not* an act of sovereignty on the same footing as amendment and abrogation; it takes a single case outside the rule, and if it becomes normal, indulgences return. It therefore exists only under these conditions: human-only, time-boxed, with a written reason, an open item in `LEDGER.md`, locks the next audit, closes only by revert or amendment, and is mandatorily inspected. It is not a ruling; it is **identity debt**. Its friction is deliberate.

**An emergency exception is not a normative source.** It cannot be cited, cannot serve as isnad, cannot be used as the rationale for a ruling or a sub-book clause, and creates no precedent. "It was done before" is not an argument.

```
CANON > SUB-BOOK > ACTIVE RULING            normative corpus

LEDGER (exceptions, tolerated deviations)   ≠ normative corpus; data, not norm
```

### 3.2 Lead — agent

Designs, produces, proposes code. Has a vote in the Council; cannot make canon-tier changes or new norms alone. Its bias is to finish the job, and this is accepted deliberately — the Guardian provides the balance.

Before building, for every question that changes what the product is, the Lead asks the Guardian: *"Is this in the canon? In a sub-book?"* If the answer is "ambiguous", it prepares an interpretation proposal and takes it to the Council; if "gap", it goes to the Master. Questions that do not change what the product is — "how" questions — are the Lead's own decisions and are written into technical documents (§2.4).

**The Lead knows the canon; it just cannot rule on its own compliance.** The canon sits verbatim in the Lead's context. When splitting a task, the Lead uses the sub-book map itself and hands the relevant clauses — copied, not summarized — to the subagent together with the task. Compliance is largely achieved during construction; the gate is the last line, not the first. The Lead may check itself; it may not approve itself.

**Conflict-of-interest rule.** If the Lead hits the canon while building a feature, it cannot propose an amendment in the same session. The proposal is queued, the PR waits, and the Council looks at it in a separate session — without the pressure of that PR.

### 3.3 Guardian — agent

Its only purpose is to serve the canon. No attachment to any feature, deadline, or sprint goal. A romantic description, but a functional one: persona steers behavior, and a character "whose only loyalty is to the canon" is a good prompt aid against builder bias. An aid, not the protection: the protection is context isolation and calibration (§7). Persona cannot be measured; those two can.

**Independence is not character; it is context design.**

```
The Guardian sees:
  canon · relevant sub-books · ACTIVE rulings · diff · read-only repo
  normalized intent — one line, the purpose of the change

The Guardian does not see:
  deadline · business value · the Lead's rationale · PR description · defense
  LEDGER — never at the gate; at audit as data, not as norm
```

Intent is necessary: seeing only a diff makes it hard to tell whether a behavior is the purpose or a side effect. But the Lead **does not write** the intent — if the Lead writes it, the persuasion channel returns. Intent derives from the assignment that precedes the Lead (the task given by the Master, the ticket); there is no rationale field.

**Its authority is asymmetric: veto only.** It can stop; it cannot steer. It cannot add a clause to the canon, cannot add to a sub-book alone, cannot issue a ruling alone. A passionate agent without initiative is what makes it safe — inquisitions begin with initiative.

**It interprets, but does not create norms.** The precise form of this boundary:

```
allowed   — norm interpretation:
  "By C-09's 'distinct interaction surface' principle, this change
   blurs the boundary between Everyday and Operator."

forbidden — norm creation:
  "Because of C-09, the Everyday surface may have at most three buttons."
```

The first interprets by citing an existing clause. The second brings a non-existent clause into being. When the Guardian is unsure whether its own reading is interpretation or creation, the default is not to interpret: NEEDS-RULING, to the Council.

**Passion must be for the canon, not for prohibition.** The canon also says what the product *is*. A guardian that only says "no" serves prohibition, not the canon. The Guardian also flags a change that violates no clause but diminishes the product's character — but **only as ADVISORY**; a feeling that cannot be cited cannot be a BLOCK.

**The four-answer rule.** To "is this in the canon?" there are four answers: **present** (cite), **contrary** (cite), **ambiguous** (cite — the clause exists, its application to this case is unclear → NEEDS-RULING, Council), **gap** (no cite — no applicable clause → NEEDS-NORM, Master). There is no clause that cannot be cited; a hallucinated clause is the most dangerous error because the Lead builds against a clause that does not exist. "Ambiguous" and "gap" may only be said when the sub-books and active rulings of the relevant domains are **fully loaded**; otherwise the answer is "indeterminate" (§6).

**Two passes.** The same agent, two separate questions:

- **Guardian pass** — looks for alignment: is it faithful to the canon? It does not read holistically: it first lists the touched clauses one by one, then evaluates each separately. In a long context, a clause in the middle gets missed; enumeration breaks that. The PRESERVED section of the verdict is the output of this list. After the clause-by-clause evaluation comes a **cross-clause pass**: clauses preserved individually can produce a violation together — C-04 and C-09 can each look clean while their combination creates a new authority/surface problem. Holistic reading is not removed; it is done *after* the clause-by-clause pass. Order: clause enumeration → clause by clause → cross-clause interaction → Breaker.
- **Breaker pass** — looks for counterexamples: it looks faithful, how do I break it? Can I bypass the authority model? Does the UI build a wrong mental model? Does this abstraction make out-of-canon behavior easier later?

Every verified counterexample from the Breaker becomes a **permanent regression artifact**: a unit/integration test, a golden semantic case, a UI eval fixture, a scenario test, a snapshot + rubric. Not all can be executable tests; all become permanent (concrete example: §9.6). Hard invariants thus sink over time into mechanical checks, and the Guardian's load narrows to its real job — the soft identity principles.

### 3.4 Inspector — agent

Who guards the Guardian? An agent reporting to the Master that audits what the Lead and the Guardian have done. It arrives unannounced, inspects, leaves.

**It audits the process, not the content.** The Guardian's AUDIT loop audits the product against the canon; the Inspector audits the agents against the **authority map**. It does not say "this PR violates C-04" — the moment it does, it is a second Guardian and produces correlated opinion. What it says is: "The Guardian passed this PR without a Breaker pass." The internal-audit vs line-management distinction.

**Zero authority, one output: a report.** No veto, no edits, no vote in the Council. The "who inspects the inspector" regress only stops when the Inspector has authority over nothing.

**It reports to the Master, but it also reports on the Master.** It must be able to say "the Master made three overrides without reasons." The tie is a reporting line, not loyalty.

**Its independence comes from context.** It is never in the same session as the Lead and the Guardian; it looks at artifacts: verdicts, `RULINGS.md`, `LEDGER.md`, session transcripts, the inputs the Guardian received. A different model family does *not* provide independence; it is a diversity heuristic used to reduce the risk of correlated blind spots.

**Inspection list:**

- Does every BLOCK have a cite + counterexample
- "Present" answers are sampled: does the cited clause actually say that
- DERIVED classifications are sampled: genuinely derivable, or a hidden new norm. The method is **blind re-derivation**: a clean Guardian instance is given only the canon clause + the sub-book clause, not the isnad text; "does this follow from that?" If it cannot be derived without seeing the argument, it is not DERIVED
- Was an amendment proposal opened in the same session as the PR that triggered it
- Is every override reasoned and logged; are overrides effectively breaching the canon
- The decisions the Lead made on its own as "operational" are sampled: do they really not change what the product is
- Did emergency exceptions close within their window
- Did rationale, PR description, or deadline leak into the Guardian's context
- Same verdict when the same PR is re-run
- Is the Ledger accumulating while the audit lags
- Is golden-set precision falling, is the override rate rising
- Sub-book clauses without isnad, recurring rulings not promoted, stale rulings not expired

**Unannounced and sampled.** Random sampling + periodic. Tax-audit logic.

What it really detects is **capture**: the Guardian being persuaded, softening, or the Lead learning to write "compliant-looking" PRs. The Guardian cannot see these in itself.

### 3.5 Council

Lead + Guardian; the Master when needed. The Council performs three operations: DERIVED sub-book clauses, interpretive rulings, gap detection. Tie → status quo.

### 3.6 Adding agents

While working, the Lead may find that a new agent is needed. There are two kinds, with different paths.

**Tool agent** — a subagent a role spins up to split its own work: a test writer, a refactorer, a domain-specific reviewer. The role opens it freely; this is not a role, it is that role's own hand. One rule:

> **Authority can be delegated, not amplified.** A subagent's authority is a subset of its parent's.

Concretely: the Lead's subagent cannot veto, cannot talk to the Guardian directly, its output counts as the Lead's output, and it cannot enter the gate as a separate "approval" — "agent X approved it" is not evidence, it is the Lead's argument, and the Guardian does not see it anyway. The Guardian's domain helper cannot create norms; the verdict is the Guardian's. The Inspector's helpers have zero authority.

**Authority-holding agent** — a role that opens a new row in the authority map: a separate security reviewer, a separate guardian for a particular sub-book, a second lead. Because the authority clause lives inside the canon, this is a **canon-tier** change:

1. The Lead proposes in a separate session — the conflict-of-interest rule applies as is; not in the session where "we needed it for this PR."
2. The Council tests the proposal against the invariant:
   - Does the new agent gather two of *create / apply / approve* in one hand?
   - Does it duplicate the Guardian? A second guardian is not a second opinion, it is a correlated one.
   - Does it breach context isolation — open a new channel from the Lead to the Guardian?
3. The Master ratifies.
4. An authority clause is added to the canon, the agent gets its own persona file, and the Inspector's list gets a new row.

If what is missing is not an agent but a **detail**, the path is already defined: DERIVED → Council, NEW NORM → Master.

---

## 4. Authority map

| Operation | Proposes | Decides | Ratifies | Record |
|---|---|---|---|---|
| Feature / PR | Lead | Guardian gate: canon objection present / absent | — | PR |
| Ruling — ambiguous norm | Lead | Council interprets (cite mandatory) | Master may recall | `RULINGS.md` |
| Gap — no norm | Guardian says "gap" | — | **Master**: NEW NORM in a sub-book or amendment | Sub-book / `CANON.md` |
| Sub-book — DERIVED | Lead | Guardian verifies isnad | — | Sub-book + isnad |
| Sub-book — NEW NORM | Lead | Council | **Master** | Sub-book + isnad |
| Canon amendment | Lead (separate session) | Council agrees | **Master** | `CANON.md` (supersedes) |
| Veto override — interpretive error | Guardian vetoes | — | **Master** (with reason) | `RULINGS.md` |
| Veto — genuine violation | Guardian vetoes | — | no override; amendment or emergency exception | `CANON.md` / `LEDGER.md` |
| Emergency exception | Master | — | Master | `LEDGER.md` (time-boxed, locks audit) |
| Apocrypha declaration | Anyone | Council | Master | Canon map |
| Opening a tool agent | The role | — (authority ≤ parent) | — | Session log |
| New authority-holding agent / role | Lead (separate session) | Council tests against the invariant | **Master** | `CANON.md` authority clause + persona file |
| Inspection | Master / periodic | Inspector reports (no authority) | — | `INSPECTIONS.md` |

Two critical rows: in a canon amendment the Master ratifies **even if the Council agrees** — two agents agreeing is more dangerous than two agents disagreeing; disagreement flags itself, agreement is silent. And a veto override overrides the Guardian; the canon changes only by amendment.

### 4.1 Two frequent objections

**"The Master becomes a bottleneck."** The Master does not make every decision; only new norms, canon-tier changes and appeals. Interpretive rulings stay in the Council, with the Master holding a right of recall (§2.3). ADVISORY does not stop a merge. The remaining wait is deliberate: identity decisions are rare and worth waiting for. If they come often, that is a canon problem, not a Master problem — there is a gap, and the override rate measures it (§7). The target metric is not the number of PRs the Master reads but the number of identity decisions made (§11).

**"Isnads get fabricated."** Three defenses at three separate levels: mechanical — does the referenced clause exist, is it abrogated, does the text match verbatim (CI); semantic — blind re-derivation; a clause that cannot be derived without seeing the argument is not DERIVED (§3.4); authority — a clause that cannot be derived is a NEW NORM and goes to the Master (§2.2). A fabricated isnad pays off only if it gets past all three.

---

## 5. Five loops

```
1. CONSULT   build-time     Lead → Guardian: "is it there?"   → present / contrary / ambiguous → Council / gap → Master
2. GATE      PR-time        Guardian → verdict                → GO / NO-GO / NEEDS-RULING / INDETERMINATE
3. AUDIT     periodic       Guardian → whole system vs canon  → drift report
4. COUNCIL   separate       Council → ruling / sub-book / amendment
5. INSPECT   unannounced    Inspector → agents vs authority map → inspection report
```

The gate sees a diff, not a trajectory; the audit looks at the trajectory. The audit inspects the product; inspect inspects the agents. All three are separate loops.

---

## 6. Verdict format

A **verdict** is one of four values; **findings** have their own severity. The two are not mixed.

```
Verdict
  GO              no violation
  NO-GO           a citable clause was violated (at least one BLOCK)
  NEEDS-RULING    a norm exists, its application to this case is unclear; cite mandatory → Council
  NEEDS-NORM      corpus fully loaded, no applicable norm → Master
  INDETERMINATE   the required corpus/context could not be established — not "gap", "could not look" → complete context, gate again

Severity
  BLOCK           cite + reproducible counterexample mandatory
  ADVISORY        drift, character, interpretation — goes to the LEDGER, does not stop the merge
  OBSERVATION     information; no action
```

`NEEDS-RULING`, `NEEDS-NORM` and `INDETERMINATE` are three different things: the first goes to the Council, the second to the Master, the third to nobody — the Guardian completes its own context and runs again. Without these distinctions, a retrieval failure disguises itself as "the canon is silent", and a gap disguises itself as "ambiguity".

`GO` is not a code review or a product approval; it means only that no canon objection was found within the normative scope examined. Security, tests and ordinary code review keep their own gates outside CDD; the Guardian is not the body that approves a feature, it is the body that objects.

Example:

```
CANON REVIEW · PR #412

Verdict: NO-GO

PRESERVED
  ✓ C-04   operator authority remains server-derived
  ✓ C-11   single-master invariant preserved

FINDINGS
  ✗ BLOCK       C-04     `is_admin_req` fallback accepts a client-originated authority hint
                         counterexample : stale client role=master → legacy path X
                         reproducible   : yes — tests/canon/test_no_client_role_fallback.py
  ⚠ ADVISORY    S-SURF-03  member-management screen moves an Operator responsibility into Everyday
                         → LEDGER
  ⚠ ADVISORY    C-09 (interpretation)  Everyday's distinct character is blurred by three new notifications
                         → LEDGER
  · OBSERVATION  "bulk role assignment": C-09 applies (management belongs on the Operator surface)
                         but the bounds of bulk assignment are unclear → NEEDS-RULING, Council, R-047

COMPLIANCE CONDITION
  No client-originated authority hint may reach an authority decision path.
  How to achieve this is the Lead's decision.
  If it cannot be achieved: C-04 amendment queue in a separate session — Master ratification required.
```

`COMPLIANCE CONDITION` replaces the old "REQUIRED" field. The Guardian does not say how to implement; it says **what the compliant state is**. Only this keeps the veto-only principle clean.

---

## 7. Calibrating the Guardian

An LLM given the objective "look for reasons to break this" invents reasons. This is the inverse of sycophancy and just as real. If the Guardian sticks an ADVISORY on every PR, within three weeks everyone turns it off like a linter.

- **Golden set.** A set of known violation / non-violation PRs; precision and recall are measured. The Guardian is a judge, and judges are meta-evaluated.
- **Override rate is a canon signal, not a Guardian error.** If the Master overrides often, there is a gap in the canon. The Guardian does not learn "not to veto" from overrides; it stays calibrated to the canon. When the canon changes, the Guardian changes — loyalty, not stubbornness.
- **Persuasion test.** What is measured is not "does the verdict change when the PR description is provided"; a verdict may rightly change with more real information. What is measured: does **neutral intent vs persuasive framing** produce different verdicts on the same diff.
- **Nondeterminism policy.** LLM verdicts are stochastic; a CI gate cannot be. Three kinds of evidence are not mixed: **grounding** (cite + reproducible counterexample) is correctness evidence; **N-run** is stability evidence — 3/3 of the same wrong interpretation is possible; the **golden set** is judge-quality evidence. Self-reported confidence is none of these and is not made a mandatory field.

  ```
  deterministic violation        → test; the Guardian is not asked
  explicit semantic violation    → BLOCK requires cite + reproducible counterexample;
                                   N runs measure stability only, inconsistent → INDETERMINATE
  character / drift              → ADVISORY + LEDGER; never BLOCK
  model instability              → INDETERMINATE; a coin flip does not stop a merge
  ```

- **Severity discipline.** BLOCK costs human time; ADVISORY goes to the ledger. A Guardian that mixes the two loses its credibility.
- **The gate is two-stage.** The mechanical gate runs first: `tests/canon/`, lint, ArchUnit-style rules. If there is a mechanical BLOCK, the Guardian does not run at all. The Guardian looks only at diffs that passed the mechanical gate, and only for principles that cannot be mechanized. Token cost and the inconsistency surface shrink together.

---

## 8. Institutional failure modes

> The mappings below make no claim to explain the causes of historical events. Old institutions built around interpretive authority — law, religion, constitutions — are used here as a **governance stress-test library**: how the same structure broke over centuries, and where the same break enters CDD.

| Institutional failure pattern | CDD failure mode | Defense |
|---|---|---|
| Dispersed interpretive authority | Every agent interprets the canon on its own; parallel interpretive traditions form | Sub-books + ACTIVE rulings: interpretation is shared |
| Capture of interpretive authority | An institutionalized interpreter grows its own authority; the Guardian becomes a de facto lawmaker | Veto-only; cannot create norms; Council; the Master's right of recall |
| Unauthorized amendment | The shared normative text changes without agreement on who may change it; implicit lex posterior | Explicit supersedes + Master ratification; intra-canon conflict closes the gate |
| The source owner breaching the norm case by case | The Master gets past the canon by ruling; the canon loses its binding force | The Master changes the canon by amendment/abrogation, never breaches it by ruling |
| Normalization of the exception | A frictionless waiver effectively breaches the canon | Time-boxed identity debt; not citable; locks the audit |
| The interpretive layer overshadowing the source norm | A sub-book produces norms the canon never stated; overrides the canon via lex specialis | DERIVED / NEW NORM; lex specialis only at the same level |
| Freezing of precedent | The ruling log turns into an immutable statute book | Lifecycle; promotion / expiry; an ACTIVE ruling is temporary authority |
| Transmission error | An agent takes the canon into context as a summary; variants multiply | Verbatim rule |
| Enforcement excess | An overzealous Guardian produces false violations; "compliant-looking" PRs get learned | Mandatory counterexamples, severity, calibration |
| The letter kept, the spirit lost | A sub-book reinterprets the canon into something else without contradicting it | Character check, cross-clause pass, ADVISORY |
| Silent consensus of the interpreters | Lead + Guardian correlated blind spot | Master ratification at canon tier and for new norms; blind re-derivation |
| The source norm detaching from reality | Code says X, canon says Y | Draft → Master ratification → canon → verified; apocrypha declaration |

**Historical illustrations** — as analogies, without causal claims:

- *Unauthorized amendment:* the Filioque controversy. An addition used locally in the West for centuries entered the universal text without agreement on who held the authority to change the shared creed; one side of the dispute was the text, the other was the authority.
- *Normalization of the exception:* indulgences. Once individual exceptions became institutional practice, what was sold was not the norm but its exception.
- *Freezing of precedent:* the narrative of the "closing of the gate of ijtihad". Whether it historically closed at all is contested — Hallaq questions the narrative — but the narrative itself describes the failure mode well: interpretation stops, imitation begins.
- *Dispersed interpretive authority:* the multiplication of parallel interpretive traditions after the Reformation, in the absence of a central interpretive authority. No single doctrine is the sole cause; this is the structural result.
- *Capture of interpretive authority:* the tendency of any institutionalized interpretive body — even one that defines itself as serving the source — to grow its own authority over time.
- *Transmission error:* variants multiplying in manuscript transmission, and the discipline of textual criticism born to sort them out.
- *Enforcement excess:* the Inquisition — a protective apparatus becoming a power independent of what it protects.

The most general lesson: none of these institutions was built to protect the text; they were built to settle **who holds interpretive authority**. The real problem is not the existence of the text — it is who interprets it, when an interpretation becomes a new norm, and who approves that transition. CDD's four roles are precisely the answers to those three questions; the real design decision is not the content of `CANON.md` but the authority map in §4.

---

## 9. CDD in practice

Everything above is governance; this is the daily work. Most of the time is a single loop; the other sections are that loop's exception paths.

### 9.1 The daily loop

```
Master    → gives a task (spec / ticket)
Lead      → splits it, hands out to subagents, builds
Lead      → /gate: diff to the Guardian
Guardian  → GO / NO-GO / NEEDS-RULING / NEEDS-NORM / INDETERMINATE
GO        → merge (no canon objection; other gates are separate)
NO-GO     → Lead revises against the compliance condition or appeals to the Master; /gate again
NEEDS-RULING  → Council (in Phase 0, a short round between Lead and Guardian in the same session; the Master sees the log)
NEEDS-NORM    → a one-line question to the Master; the answer is one line in a sub-book or the canon
INDETERMINATE → context is completed, /gate again; goes to nobody
```

### 9.2 Three kinds of missing, three doors

When an agent says "there is no guidance", its job is not done; it has to say which kind of guidance is missing:

```
"Should there be an undo?"                     spec gap   → the task giver (Master)
"Can an Everyday user see this?"               norm question → Guardian first (cite); if ambiguous, Council; if gap, Master
"Which transaction strategy?"                  how gap    → the Lead decides, asks nobody
```

One test: would the answer change what the product is? (§2.4)

### 9.3 Task handoff

The Lead knows the canon. When handing a task to a subagent, it copies the relevant clauses; it does not summarize them:

```
Task:       Add bulk role assignment to the Operator surface
Spec:       <ticket>
Canon:      C-04 (verbatim) · C-09 (verbatim)
Sub-book:   S-AUTH-12 (verbatim)
Bounds:     no client-originated hint reaches an authority path; nothing leaks into Everyday
```

Compliance is achieved during construction; the gate is the last line. If NO-GO comes often, either the Lead is not routing clauses or the canon is unclear — both are signals for the Master.

### 9.4 After a NO-GO

```
fix            satisfy the compliance condition, gate again; the Breaker's test stays in tests/canon/
appeal         no arguing with the Guardian, there is no channel — to the Master; if the Guardian was wrong, override + RULINGS
amendment      separate session, queued, the PR waits; Master ratifies with supersedes; the PR is re-gated against the new canon
emergency      Master only; time-boxed, LEDGER, audit locked; cannot be cited
```

What the Lead cannot do: resubmit the same diff hoping for a different roll; make it *look* compliant; open an amendment in the same session.

### 9.5 Writing the canon

- One page. If it overflows, push down into a sub-book.
- Numbered clauses; each clause one sentence, one claim.
- Definitions as much as prohibitions. Without "this product is X" clauses, the Guardian can only say "no".
- No features. "Bulk assignment exists" is not canon; "authority is server-derived" is.
- The authority clause: who interprets, who amends, what is delegated to the Council.
- The sub-book map and the apocrypha list.
- A clause proposed by the Lead is a DRAFT; it is not canon until the Master ratifies it.

### 9.6 Artifacts for soft principles

Not every counterexample becomes a test. For "this screen builds a wrong mental model", a **golden semantic case**:

```
GSC-007
  clause     : C-09
  state      : a member-management entry on the Everyday screen (screenshot or state dump)
  question   : Does this screen turn Everyday into Operator?
  expected   : ADVISORY — spirit of C-09; the boundary blurs
  rationale  : C-09 (surfaces are distinct) + S-SURF-03 (member management is an Operator responsibility) — cites only the active corpus
```

At audit time the Guardian re-evaluates these cases; deviation from the expected verdict is a calibration signal. This is the soft half of the golden set; a UI eval fixture is the same thing in scenario + rubric form.

**Golden artifacts are not normative.** The expected verdict and rationale may cite only the active normative corpus; a rationale that cannot cite does not enter a golden case — otherwise the golden set silently becomes a fourth canon. If the source clause is superseded, the related golden case is automatically invalidated. The direction is one way: canon → golden oracle; never golden oracle → canon interpretation.

### 9.7 Claude Code setup

```
CANON.md      → included verbatim in CLAUDE.md; every session starts with it
GUARDIAN.md   → the Guardian subagent prompt; it receives canon + relevant books + diff + intent
/consult      → before building; only questions that touch identity
/gate         → on the diff; mechanical gate first, then the Guardian
RULINGS.md    → one line whenever a decision is made
/council      → Phase 1;  /inspect → Phase 2
```

You start with three files and one command: `CANON.md`, `GUARDIAN.md`, `/gate`.

### 9.8 Cost

**Tokens.** One Guardian call per PR, small context: one page of canon + the relevant book + the diff. The same order of magnitude as a code-review call. N runs only for BLOCK-candidate findings, not for every PR; run across model families, they also sample against a single Guardian's blind spot. Audit is periodic, inspection is sampled. Small next to generation cost.

**Human.** This is the real cost, and it is what gets measured (§11). In Phase 0 the Master's cost is only NO-GO appeals and "absent" answers; both shrink as the canon matures.

---

## 10. Phased rollout

None of this is set up on day one. The method's own principle: layers open as rulings and drift accumulate.

**Before Phase 0 — only `CANON.md`.** In the Lead's context, no Guardian. This is not CDD; it is a Spec-Kit constitution. But it teaches you to write a canon and lets you feel the first drift — the moment you realize you need a Guardian, Phase 0 begins.

**Phase 0 — day one.** The minimum viable core.

```
CANON.md          one page · numbered clauses · authority clause · apocrypha list
GUARDIAN.md       persona · context rules · four answers · verdict format
RULINGS.md        chronological
canon-gate        the Guardian subagent on the PR, verdict as a comment, BLOCK stops the merge
```

The Master is manual. No sub-books; the canon carries everything because it is still small.

**Phase 1 — once a recurring normative theme appears in the same domain.** The default operational threshold is three ACTIVE rulings, but it is a heuristic: two rulings repeating the same problem already call for a sub-book, three unrelated ones do not. The trigger is neither a calendar nor a counter but a signal: that domain's sub-book opens and the rulings are promoted into it.

```
docs/canon/*.md   per-domain sub-books · isnad · DERIVED / NEW NORM
LEDGER.md         tolerated deviations · emergency exceptions
/council          separate session · amendment queue
tests/canon/      Breaker artifacts
```

**Phase 2 — once drift becomes visible.**

```
INSPECTOR.md + INSPECTIONS.md    the Inspector
golden set                       Guardian precision / recall
domain router                    file → sub-book + active ruling loading; "ambiguous/gap" only when fully loaded
                                 deterministic mapping (path/tag → book); semantic retrieval is never
                                 used for the normative corpus. For cross-domain effects the Guardian may
                                 request additional books; INDETERMINATE until loaded
ruling lifecycle                 ACTIVE / PROMOTED / SUPERSEDED / EXPIRED / ARCHIVED
CI policy                        N runs, INDETERMINATE
metrics                          §11
```

Claude Code mapping: the Lead is the main agent. The Guardian is a context-restricted subagent — no access to the PR description or the Lead's rationale; it takes intent from the assignment. Canon-gate is the same subagent in CI. `/council` is a separate command. `/inspect` is a separate command, preferably a different model, looking only at logs and transcripts.

---

## 11. Experiment protocol

This is not a claim of a method; it is a proposal and a plan to test it. Results are reported with metrics.

**Four primary axes:**

1. **Drift detection** — how much of the identity drift a human catches does the Guardian catch?
2. **False-block rate** — how often does it needlessly stop compliant changes?
3. **Human attention compression** — does the number of PRs the Master reads per identity decision made go down?
4. **Longitudinal consistency** — after 100–500 changes, is conformance to the canon preserved relative to the start?

**Secondary metrics:** Guardian precision / recall, override rate, verdict stability, ambiguous-case and gap rate, ruling promotion rate, stale ruling count, amendment rate, emergency-exception count and time to closure.

These metrics need at least ~100 changes before they produce data; there is nothing to measure in Phase 0.

**Test environment.** The proposal emerged in a first product, by formalizing existing practice retrospectively. It is being applied deliberately from the start in a second product. The second product must be **different in character** from the first; a second application of the same character is repetition, not generalization.

The expected outcome: if an LLM Guardian's precision on soft identity principles turns out acceptable, then separation of powers is a practical way to protect the LLM's semantic capacity from builder bias. If it does not, one falls back to mechanical fitness functions and this proposal remains an expensive layer on top of them. Either outcome is reported.

---

## References

- Ford, N., Parsons, R., Kua, P. *Building Evolutionary Architectures*. O'Reilly, 2017 — architectural fitness functions.
- Nygard, M. "Documenting Architecture Decisions", 2011 — ADR.
- Evans, E. *Domain-Driven Design*. Addison-Wesley, 2003 — ubiquitous language.
- GitHub Spec Kit — constitution artifact. https://github.com/github/spec-kit
- Marri, S. R. "Constitutional Spec-Driven Development: Enforcing Security by Construction in AI-Assisted Code Generation". arXiv:2602.02584, January 2026.
- Alenezi, M. "Specification-Driven Development as the Foundation of AI-Native Enterprise Software Engineering". arXiv:2607.16680, July 2026 — Specification Governance Reference Model.
