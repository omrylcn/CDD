#!/usr/bin/env python3
"""Operator CLI for a local, report-only CDD fixed-diff experiment."""
import argparse
import hashlib
import json
import math
import os
import random
import re
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from contextlib import closing
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ARMS = ("baseline", "guardian", "lead-self")
STAGES = ("pre", "post")
ROUTES = {"NEEDS-NORM", "NEEDS-RULING", "CONTEXT", "INSTABILITY"}
FORMAT = """Return one JSON object:
{"gate":"GO","routes":[],"blocks":[],"advisory":false,"reason":"Your scope and evidence."}
GO means complete without an explicit violation; HOLD means required work is open;
NO-GO requires a supported violation. Keep open routes even with NO-GO. Route choices
are CONTEXT (missing inputs), NEEDS-RULING (interpretation), NEEDS-NORM (new identity
decision), INSTABILITY (unexplained contradiction on fixed inputs). For each explicit
violation add {"clause":"<id>","action":"<public action>","field":"<output field>",
"value":<observed JSON scalar>} to blocks. Record soft concerns with advisory=true.
This compact observation is for measurement. It cannot serve as a production verdict.
"""
BASELINE = """Review this change using the supplied product sources, original task,
diff and runtime observations. Identify changes in product behavior. Return the
common response format. Keep the conversation available for follow-up.
"""


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def dump(data):
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False) + "\n"


def write(path, value):
    path.write_text(value, encoding="utf-8")


def digest(data):
    return hashlib.sha256(data).hexdigest()


def tree_hash(folder):
    files = {p.relative_to(folder).as_posix(): digest(p.read_bytes())
             for p in sorted(folder.rglob("*")) if p.is_file()}
    return digest(dump(files).encode())


def git(folder, *args):
    env = dict(os.environ, GIT_AUTHOR_DATE="2001-01-01T00:00:00Z",
               GIT_COMMITTER_DATE="2001-01-01T00:00:00Z")
    return subprocess.check_output(
        ["git", "-c", "user.name=CDD lab", "-c", "user.email=lab@example.invalid",
         "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
         "-c", "core.autocrlf=false", *args], cwd=folder, env=env, text=True).strip()


def build_packet(folder, case):
    folder.mkdir(parents=True)
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        shutil.copytree(HERE / "reader", repo, dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("__pycache__"))
        git(repo, "init", "-q")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "Reading desk base")
        base = git(repo, "rev-parse", "HEAD")
        policy = read(repo / "policy.json")
        policy.update(case["changes"])
        write(repo / "policy.json", dump(policy))
        if "proposed_clause" in case:
            lines = (repo / "CANON.md").read_text(encoding="utf-8").splitlines()
            write(repo / "CANON.md", "\n".join(case["proposed_clause"] if l.startswith("- **R-01.") else l for l in lines) + "\n")
        git(repo, "add", ".")
        git(repo, "commit", "-qm", "Candidate change")
        head = git(repo, "rev-parse", "HEAD")
        (folder / "change.diff").write_bytes(git_diff(repo, base, head))
        for name in ("reader.py", "policy.json"):
            shutil.copyfile(repo / name, folder / name)
    sources = folder / "base-sources"
    sources.mkdir()
    shutil.copyfile(HERE / "reader/CANON.md", sources / "CANON.md")
    if case["archive_source"]:
        shutil.copyfile(HERE / "reader/ARCHIVE.md", sources / "ARCHIVE.md")
    write(folder / "task.md", case["task"] + "\n")
    write(folder / "response-format.md", FORMAT)
    observations = {}
    for action in ("open", "preview", "finish", "suggest", "library", "archive"):
        output = subprocess.check_output([sys.executable, str(folder / "reader.py"), action], text=True)
        observations[action] = json.loads(output)
    write(folder / "observations.json", dump(observations))
    write(folder / "inputs.json", dump({
        "code_sha": head, "base_sha": base, "task_ref": digest((folder / "task.md").read_bytes()),
        "corpus_hash": tree_hash(sources), "missing_sources": [] if case["archive_source"] else ["ARCHIVE.md"],
        "source_basis": "simulation-only", "prior_consult": [],
    }))


def git_diff(repo, base, head):
    return subprocess.check_output(["git", "diff", "--no-ext-diff", "--no-textconv", "--no-color",
                                    "--no-renames", base, head, "--"], cwd=repo)


def build_external_packet(folder, case, manifest_dir):
    """Read tracked source blobs at the accepted base. Never run code from an imported diff."""
    repo = (manifest_dir / case["repo"]).resolve()
    base, head = case["base_sha"], case["code_sha"]
    for revision in (base, head):
        if (not isinstance(revision, str) or not re.fullmatch(r"[a-f0-9]{40}|[a-f0-9]{64}", revision)
                or git(repo, "rev-parse", "--verify", revision + "^{commit}") != revision):
            raise ValueError("external revisions must be complete, existing commit IDs")
    subprocess.run(["git", "merge-base", "--is-ancestor", base, head], cwd=repo, check=True)
    diff = git_diff(repo, base, head)
    if not diff:
        raise ValueError("the imported change must contain a nonempty diff")
    folder.mkdir(parents=True)
    (folder / "change.diff").write_bytes(diff)
    sources = folder / "base-sources"
    sources.mkdir()
    for name in case["sources"]:
        rel = Path(name)
        if rel.is_absolute() or not rel.parts or ".." in rel.parts:
            raise ValueError("accepted sources must be relative tracked files")
        dest = sources / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        blob = subprocess.check_output(["git", "cat-file", "blob", base + ":" + rel.as_posix()], cwd=repo)
        dest.write_bytes(blob)
    outputs = read(manifest_dir / case["observations"])
    if not isinstance(outputs, dict) or not all(isinstance(fields, dict) for fields in outputs.values()):
        raise ValueError("observations must map public actions to output-field objects")
    acceptance_ref = case["acceptance_ref"]
    if not isinstance(acceptance_ref, str) or not acceptance_ref.strip():
        raise ValueError("supply a base-bound human acceptance evidence reference")
    write(folder / "task.md", case["task"] + "\n")
    write(folder / "response-format.md", FORMAT)
    write(folder / "observations.json", dump(outputs))
    write(folder / "inputs.json", dump({"code_sha": head, "base_sha": base, "corpus_hash": tree_hash(sources),
          "task_ref": digest((folder / "task.md").read_bytes()), "source_basis": acceptance_ref,
          "missing_sources": case.get("missing_sources", []), "prior_consult": case.get("prior_consult", [])}))


def prepare(run, seed=17, split="all", repeats=1, mode="observed", token_budget=8000, manifest=None):
    if repeats < 1 or token_budget < 1:
        raise ValueError("repeats and token budget must be positive")
    if manifest is None:
        cases, labels = read(HERE / "cases.json"), read(HERE / "gold.json")
        source = "built-in fixtures; author-seeded labels"
    else:
        supplied = read(manifest)
        cases, labels, source = supplied["cases"], supplied["labels"], supplied["label_provenance"]
        if not isinstance(source, str) or not source.strip():
            raise ValueError("state where the reference labels came from")
    if {c["id"] for c in cases} != set(labels) or len(labels) != len(cases):
        raise ValueError("case IDs and reference labels must match exactly")
    families = {}
    for case in cases:
        if case["split"] not in ("calibration", "evaluation") or not case["family"]:
            raise ValueError("each case needs a family and a valid split")
        validate_observation(dict(labels[case["id"]], reason="Reference label."))
        if families.setdefault(case["family"], case["split"]) != case["split"]:
            raise ValueError("a change family crosses the calibration/evaluation split")
    included = [c for c in cases if split == "all" or c["split"] == split]
    if not included:
        raise ValueError("the selected split has no cases")
    run.mkdir(parents=True, exist_ok=False)
    try:
        operator = run / "operator"
        operator.mkdir()
        shutil.copytree(HERE / "roles", operator / "roles")
        for skill in ("cdd-guardian", "cdd-inspect"):
            shutil.copytree(ROOT / "skills" / skill, operator / "skills" / skill,
                            ignore=shutil.ignore_patterns("__pycache__"))
        write(operator / "baseline.md", BASELINE)
        trials = {}
        order = [(case, rep) for case in included for rep in range(repeats)]
        rng = random.Random(seed)
        rng.shuffle(order)
        for idx, (case, rep) in enumerate(order, start=1):
            tid = f"t{idx:03d}"
            packet = run / "packets" / tid
            if manifest is None:
                build_packet(packet, case)
            else:
                build_external_packet(packet, case, manifest.resolve().parent)
            gold = labels[case["id"]]
            if not grade(gold, gold, read(packet / "observations.json"))["exact"]:
                raise ValueError("reference witness missing from the candidate observations")
            trials[tid] = {"case": case["id"], "family": case["family"], "split": case["split"],
                           "rep": rep + 1, "digest": tree_hash(packet), "gold": labels[case["id"]],
                           "defense": case["defense"], "first_arm": rng.choice(["baseline", "guardian"])}
        write(operator / "plan.json", dump({"mode": mode, "trials": trials, "seed": seed, "source": source,
              "token_budget_per_arm": token_budget, "roles_hash": tree_hash(operator / "roles"),
              "skills_hash": tree_hash(operator / "skills"), "baseline_hash": digest(BASELINE.encode())}))
        write(operator / "plan.sha256", digest((operator / "plan.json").read_bytes()) + "\n")
        with sqlite3.connect(operator / "responses.db") as db:
            db.executescript("""
            CREATE TABLE responses (
                trial TEXT, arm TEXT, stage TEXT, session TEXT, model TEXT, result TEXT,
                tokens INTEGER, seconds REAL, human_minutes REAL, packet_digest TEXT,
                PRIMARY KEY(trial, arm, stage));
            CREATE TABLE authors (trial TEXT PRIMARY KEY, session TEXT, code_sha TEXT, evidence TEXT);
            """)
    except BaseException:
        shutil.rmtree(run)
        raise


def read_plan(run):
    path = run / "operator/plan.json"
    if digest(path.read_bytes()) != (run / "operator/plan.sha256").read_text().strip():
        raise ValueError("the operator plan differs from its prepared digest")
    return read(path)


def plan_trial(run, trial):
    plan = read_plan(run)
    if trial not in plan["trials"]:
        raise ValueError("unknown trial ID")
    return plan, plan["trials"][trial]


def verify_packet(run, trial):
    plan, row = plan_trial(run, trial)
    if tree_hash(run / "packets" / trial) != row["digest"]:
        raise ValueError("packet differs from the frozen trial")
    op = run / "operator"
    if (tree_hash(op / "roles") != plan["roles_hash"] or tree_hash(op / "skills") != plan["skills_hash"]
            or digest((op / "baseline.md").read_bytes()) != plan["baseline_hash"]):
        raise ValueError("review instructions differ from the frozen plan")
    return plan, row


def export(run, trial, arm, dest):
    verify_packet(run, trial)
    if dest.exists():
        raise ValueError("export needs a new directory")
    op = run / "operator"
    shutil.copytree(run / "packets" / trial, dest)
    if arm == "guardian":
        shutil.copytree(op / "skills/cdd-guardian", dest / ".claude/skills/cdd-guardian")
        shutil.copytree(op / "skills/cdd-guardian", dest / ".agents/skills/cdd-guardian")
        roles = dest / ".claude/agents"
        roles.mkdir(parents=True)
        shutil.copyfile(op / "roles/cdd-guardian.md", roles / "cdd-guardian.md")
        simulated = read(dest / "inputs.json")["source_basis"] == "simulation-only"
        note = ("The exercise assumes the base sources only for simulation." if simulated else
                "Read the referenced acceptance evidence in inputs.json.")
        write(dest / "ASSIGNMENT.md", (op / "roles/cdd-guardian.md").read_text(encoding="utf-8")
              + "\n" + note + " Use the compact response format.\n")
    else:
        shutil.copyfile(op / "baseline.md", dest / "ASSIGNMENT.md")


def validate_observation(result):
    if not isinstance(result, dict) or result.get("gate") not in ("GO", "HOLD", "NO-GO"):
        raise ValueError("observation needs a valid gate")
    routes, blocks = result.get("routes"), result.get("blocks")
    if not isinstance(routes, list) or any(not isinstance(x, str) or x not in ROUTES for x in routes):
        raise ValueError("invalid routes")
    if len(set(routes)) != len(routes) or not isinstance(blocks, list):
        raise ValueError("duplicate routes or invalid blocks")
    for item in blocks:
        if (not isinstance(item, dict) or set(item) != {"clause", "action", "field", "value"}
                or any(not isinstance(item[k], str) or not item[k].strip() for k in ("clause", "action", "field"))
                or not isinstance(item["value"], (str, int, float, bool, type(None)))
                or isinstance(item["value"], float) and not math.isfinite(item["value"])):
            raise ValueError("invalid observable BLOCK witness")
    if type(result.get("advisory")) is not bool or not isinstance(result.get("reason"), str) or not result["reason"].strip():
        raise ValueError("supply advisory boolean and a written reason")
    if (result["gate"] == "NO-GO") != bool(blocks) or (result["gate"] == "GO" and routes):
        raise ValueError("gate contradicts submitted findings or open routes")


def connect(run):
    db = sqlite3.connect(run / "operator/responses.db", timeout=10)
    db.row_factory = sqlite3.Row
    return db


def enter(run, trial, arm, stage, session, model, result, tokens=None, seconds=None, human_minutes=None):
    _, meta = verify_packet(run, trial)
    validate_observation(result)
    if arm not in ARMS or stage not in STAGES or not session.strip() or not model.strip():
        raise ValueError("invalid arm, stage, session or model")
    if any(x is not None and (not math.isfinite(x) or x < 0) for x in (tokens, seconds, human_minutes)):
        raise ValueError("usage values must be finite and nonnegative")
    with connect(run) as db:
        db.execute("BEGIN IMMEDIATE")
        old = db.execute("SELECT * FROM responses WHERE session=?", (session,)).fetchall()
        if any(x["trial"] != trial or x["arm"] != arm for x in old):
            raise ValueError("separate trials and arms require separate sessions")
        author = db.execute("SELECT session FROM authors WHERE trial=?", (trial,)).fetchone()
        is_author = bool(author and author["session"] == session)
        if (arm == "lead-self") != is_author:
            raise ValueError("the recorded author uses only lead-self; other roles need separate sessions")
        if stage == "post":
            prior = db.execute("SELECT * FROM responses WHERE trial=? AND arm=? AND stage='pre'",
                               (trial, arm)).fetchone()
            if not prior or (session, model) != (prior["session"], prior["model"]):
                raise ValueError("post requires the same prior session and model")
        db.execute("INSERT INTO responses VALUES (?,?,?,?,?,?,?,?,?,?)",
                   (trial, arm, stage, session, model, dump(result), tokens, seconds, human_minutes, meta["digest"]))


def defense(run, trial, arm, session):
    _, meta = verify_packet(run, trial)
    with connect(run) as db:
        row = db.execute("SELECT session FROM responses WHERE trial=? AND arm=? AND stage='pre'",
                         (trial, arm)).fetchone()
    if not row or row["session"] != session:
        raise ValueError("record the initial response before requesting the defense in the same session")
    return meta["defense"]


def bind_author(run, trial, session, evidence, head):
    verify_packet(run, trial)
    if head != read(run / "packets" / trial / "inputs.json")["code_sha"] or not session.strip() or not evidence.strip():
        raise ValueError("bind the verified candidate head, author session and an external evidence reference")
    with connect(run) as db:
        db.execute("BEGIN IMMEDIATE")
        if db.execute("SELECT 1 FROM responses WHERE trial=?", (trial,)).fetchone():
            raise ValueError("register authorship before any response for the trial")
        db.execute("INSERT INTO authors VALUES (?,?,?,?)", (trial, session, head, evidence))


def grade(observation, gold, outputs):
    """Require the named clause and the publicly observable counterexample."""
    def witness_set(blocks):
        return {dump(block) for block in blocks}

    observed = observation["blocks"]
    real_witnesses = all(b["field"] in outputs.get(b["action"], {})
                         and dump(outputs[b["action"]][b["field"]]) == dump(b["value"])
                         for b in observed)
    findings_correct = real_witnesses and witness_set(observed) == witness_set(gold["blocks"])
    gate_correct = observation["gate"] == gold["gate"]
    return {
        "exact": gate_correct and findings_correct and set(observation["routes"]) == set(gold["routes"])
                 and observation["advisory"] == gold["advisory"],
        "gate_correct": gate_correct,
        "detected": gold["gate"] == "NO-GO" and observation["gate"] == "NO-GO" and findings_correct,
    }


def fraction(numerator, denominator):
    return {"n": numerator, "of": denominator,
            "rate": round(numerator / denominator, 4) if denominator else None}


def summarize_group(rows, planned):
    count = len(rows)
    compliant = [r for r in rows if r["expected"] == "GO"]
    violating = sum(r["expected"] == "NO-GO" for r in rows)
    predicted = sum(r["gate"] == "NO-GO" for r in rows)
    correct = sum(r["detected"] for r in rows)
    return {
        "coverage": fraction(count, planned),
        "exact": fraction(sum(r["exact"] for r in rows), count),
        "precision": fraction(correct, predicted), "recall": fraction(correct, violating),
        "false_block": fraction(sum(r["gate"] == "NO-GO" for r in compliant), len(compliant)),
        "hold": fraction(sum(r["gate"] == "HOLD" for r in rows), count),
        "wrong_evidence_on_violations": sum(r["gate"] == r["expected"] == "NO-GO"
                                            and not r["detected"] for r in rows),
    }


def score(run):
    plan = read_plan(run)
    with closing(connect(run)) as db:
        responses = list(db.execute("SELECT * FROM responses ORDER BY trial, arm, stage"))
    results, paired, spending = [], {}, {}
    outputs = {}
    for trial in plan["trials"]:
        verify_packet(run, trial)
        outputs[trial] = read(run / "packets" / trial / "observations.json")
    for row in responses:
        trial, arm, stage = row["trial"], row["arm"], row["stage"]
        meta = plan["trials"][trial]
        result = json.loads(row["result"])
        evaluated = grade(result, meta["gold"], outputs[trial])
        entry = {"trial": trial, "family": meta["family"], "split": meta["split"], "arm": arm,
                 "stage": stage, "gate": result["gate"], "expected": meta["gold"]["gate"], **evaluated}
        results.append(entry)
        paired[trial, arm, stage] = entry
        spending.setdefault((trial, arm), {})[stage] = row
    groups = {a: {s: summarize_group([r for r in results if r["arm"] == a and r["stage"] == s],
                                     len(plan["trials"])) for s in STAGES} for a in ARMS}
    # The Lead's own pre-defense review is the fixed reference for both Guardian stages.
    lead_misses = [r["trial"] for r in results if r["arm"] == "lead-self" and r["stage"] == "pre"
                   and r["expected"] == "NO-GO" and r["gate"] == "GO"]
    shared = {}
    for stage in STAGES:
        linked = [paired[t, "guardian", stage] for t in lead_misses if (t, "guardian", stage) in paired]
        numerator = sum(r["gate"] == "GO" for r in linked)
        missing = len(lead_misses) - len(linked)
        shared[stage] = {"lead_go_violations": len(lead_misses), "unpaired": missing,
                         **fraction(numerator, len(linked))}
        if missing:
            shared[stage]["rate"] = None
    cost, dialogue = [], []
    for (trial, arm), stages in sorted(spending.items()):
        if all(s in stages for s in STAGES):
            pre, post = (paired[trial, arm, s] for s in STAGES)
            dialogue.append({"trial": trial, "arm": arm, "pre_exact": pre["exact"], "post_exact": post["exact"],
                             "gate_changed": pre["gate"] != post["gate"]})
        totals = {}
        for field in ("tokens", "seconds", "human_minutes"):
            values = [row[field] for row in stages.values()]
            totals[field] = sum(values) if len(values) == len(STAGES) and None not in values else None
        totals["over_token_budget"] = (None if totals["tokens"] is None else
                                       totals["tokens"] > plan["token_budget_per_arm"])
        cost.append({"trial": trial, "arm": arm, **totals})
    return {"mode": plan["mode"], "planned_trials": len(plan["trials"]), "observations": len(results),
            "source": plan.get("source", "built-in fixtures"), "token_budget_per_arm": plan["token_budget_per_arm"],
            "scores": groups, "shared_miss": shared, "dialogue": dialogue, "usage": cost, "rows": results}


def audit_packet(run, trial, dest):
    _, meta = verify_packet(run, trial)
    if dest.exists():
        raise ValueError("audit export needs a new directory")
    shutil.copytree(run / "packets" / trial, dest)
    op = run / "operator"
    shutil.copyfile(op / "roles/cdd-inspector.md", dest / "ASSIGNMENT.md")
    shutil.copytree(op / "skills/cdd-inspect", dest / ".agents/skills/cdd-inspect")
    with closing(connect(run)) as db:
        rows = list(db.execute("SELECT * FROM responses WHERE trial=? ORDER BY arm, stage DESC", (trial,)))
    records = [{**dict(r), "result": json.loads(r["result"])} for r in rows]
    # A missing defense stays missing until at least one post-defense record exists.
    write(dest / "decision-trail.json", dump({"trial": trial, "records": records,
          "defense": meta["defense"] if any(r["stage"] == "post" for r in rows) else None}))


def smoke():
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "run"
        prepare(run, mode="scripted")
        for trial, meta in read_plan(run)["trials"].items():
            response = dict(meta["gold"], reason="Scripted plumbing check.")
            for stage in STAGES:
                enter(run, trial, "guardian", stage, trial, "scripted", response)
        measured = score(run)
        end = measured["scores"]["guardian"]["post"]["exact"]
        if end["n"] != len(measured["rows"]) // 2 or end["rate"] != 1:
            raise ValueError("scripted records do not match the frozen outputs")
        print(f"Scripted plumbing check: {end['n']}/{end['of']} cases; {measured['observations']} records.")


def package_plugin(dest):
    """Assemble optional Claude Code distribution from the canonical repository files."""
    dest.mkdir(parents=True, exist_ok=False)
    try:
        (dest / ".claude-plugin").mkdir()
        write(dest / ".claude-plugin/plugin.json", dump({
            "name": "cdd-phase0", "description": "CDD project roles and review skills for a shadow pilot.",
            "version": "0.1.0"}))
        shutil.copytree(HERE / "roles", dest / "agents")
        for name in ("cdd-init", "cdd-guardian", "cdd-inspect"):
            shutil.copytree(ROOT / "skills" / name, dest / "skills" / name,
                            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"))
    except BaseException:
        shutil.rmtree(dest)
        raise


def replay_sample():
    sample = read(HERE / "observed-sample.json")
    with tempfile.TemporaryDirectory() as tmp:
        run = Path(tmp) / "run"
        prepare(run, seed=sample["seed"], split=sample["split"], mode="archived observations replay")
        plan = read_plan(run)
        for row in sample["records"]:
            meta = plan["trials"][row["trial"]]
            if meta["case"] != row["case"] or meta["digest"] != row["packet_digest"]:
                raise ValueError("the published observation refers to a different review packet")
            enter(run, row["trial"], row["arm"], row["stage"], row["session"], row["model"], row["result"],
                  row["tokens"], row["seconds"], row["human_minutes"])
        return score(run)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    prep = commands.add_parser("prepare", help="freeze an operator run in a new directory")
    prep.add_argument("run", type=Path)
    prep.add_argument("--seed", type=int, default=17)
    prep.add_argument("--repeats", type=int, default=1)
    prep.add_argument("--token-budget", type=int, default=8000)
    prep.add_argument("--split", choices=("calibration", "evaluation", "all"), default="all")
    prep.add_argument("--manifest", type=Path, help="operator-authored real-product case manifest")
    for name in ("list", "export", "submit", "defense", "score", "bind-author", "audit-packet"):
        sub = commands.add_parser(name)
        sub.add_argument("run", type=Path)
        if name not in ("list", "score"):
            sub.add_argument("trial")
        if name in ("export", "submit", "defense"):
            sub.add_argument("arm", choices=ARMS)
        if name in ("export", "audit-packet"):
            sub.add_argument("--out", type=Path, required=True)
        if name in ("submit", "defense", "bind-author"):
            sub.add_argument("--session", required=True)
        if name == "submit":
            sub.add_argument("stage", choices=STAGES)
            sub.add_argument("--model", required=True)
            sub.add_argument("--response", type=Path, required=True)
            sub.add_argument("--tokens", type=int)
            sub.add_argument("--seconds", type=float)
            sub.add_argument("--human-minutes", type=float)
        if name == "bind-author":
            sub.add_argument("--head", required=True)
            sub.add_argument("--evidence", required=True)
    commands.add_parser("smoke", help="exercise the plumbing with seeded responses, without an agent")
    commands.add_parser("replay-sample", help="re-score archived observations on regenerated packets")
    pack = commands.add_parser("package-plugin", help="assemble a local Claude Code plugin")
    pack.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        if args.command == "smoke":
            smoke()
        elif args.command == "replay-sample":
            print(dump(replay_sample()), end="")
        elif args.command == "package-plugin":
            package_plugin(args.out)
        elif args.command == "prepare":
            prepare(args.run, args.seed, args.split, args.repeats, token_budget=args.token_budget, manifest=args.manifest)
        elif args.command == "list":
            for trial, meta in read_plan(args.run)["trials"].items():
                print(trial, meta["split"], "first:", meta["first_arm"])
        elif args.command == "export":
            export(args.run, args.trial, args.arm, args.out)
        elif args.command == "submit":
            enter(args.run, args.trial, args.arm, args.stage, args.session, args.model, read(args.response),
                  args.tokens, args.seconds, args.human_minutes)
        elif args.command == "defense":
            print(defense(args.run, args.trial, args.arm, args.session))
        elif args.command == "bind-author":
            bind_author(args.run, args.trial, args.session, args.evidence, args.head)
        elif args.command == "audit-packet":
            audit_packet(args.run, args.trial, args.out)
        else:
            print(dump(score(args.run)), end="")
    except (ValueError, OSError, KeyError, TypeError, sqlite3.Error, subprocess.SubprocessError) as exc:
        parser.exit(1, f"{exc}\n")


if __name__ == "__main__":
    main()
