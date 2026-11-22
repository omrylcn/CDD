"""Replay two archived reading-desk patches, their observations and paired reviews."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))
import lab

BASE_FILES = ("ARCHIVE.md", "CANON.md", "policy.json", "reader.py")
BASE_ACTIONS = ("open", "preview", "finish", "suggest", "library", "archive")
ARMS = ("lead-self", "guardian")


def check(actual, expected, label):
    if actual != expected:
        raise ValueError(f"{label}: expected {expected!r}, observed {actual!r}")


def install_commit(repo, saved):
    """Bind the reconstructed index to the original commit, including its metadata."""
    body = saved["git_object"]
    check(body.splitlines()[0], "tree " + lab.git(repo, "write-tree"), "fixture tree")
    sha = subprocess.check_output(
        ["git", "hash-object", "-w", "-t", "commit", "--stdin"],
        cwd=repo, input=body, text=True,
    ).strip()
    check(sha, saved["sha"], "fixture commit")
    lab.git(repo, "update-ref", "HEAD", sha)


def restore_base(repo, revision, saved):
    repo.mkdir()
    lab.git(repo, "init", "-q")
    has_history = subprocess.run(
        ["git", "cat-file", "-e", revision + "^{commit}"], cwd=lab.ROOT,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    ).returncode == 0
    for name in BASE_FILES:
        target = repo / name
        if has_history:
            blob = f"{revision}:experiments/phase0/reader/{name}"
            target.write_bytes(subprocess.check_output(["git", "cat-file", "blob", blob], cwd=lab.ROOT))
        else:
            shutil.copyfile(lab.HERE / "reader" / name, target)
    lab.git(repo, "add", "--", *BASE_FILES)
    install_commit(repo, saved)


def observe(repo, action):
    output = subprocess.check_output([sys.executable, "-B", "reader.py", action], cwd=repo, text=True)
    return json.loads(output)


def check_configured_resume(repo, sample, scratch):
    scratch.mkdir()
    shutil.copyfile(repo / "reader.py", scratch / "reader.py")
    policy = lab.read(repo / "policy.json")
    policy.update(sample["policy_overrides"])
    lab.write(scratch / "policy.json", lab.dump(policy))
    for action in ("open", "resume"):
        check(observe(scratch, action), sample["observed"], f"configured {action}")


def evaluator_id(revision, fallback):
    listing = subprocess.run(
        ["git", "ls-tree", "-rz", revision + ":skills/cdd-guardian"],
        cwd=lab.ROOT, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    if listing.returncode:
        digest = lab.tree_hash(fallback)
    else:
        hashes = {}
        for entry in listing.stdout.split(b"\0")[:-1]:
            metadata, name = entry.split(b"\t", 1)
            blob = metadata.split()[2].decode()
            data = subprocess.check_output(["git", "cat-file", "blob", blob], cwd=lab.ROOT)
            hashes[name.decode()] = lab.digest(data)
        digest = lab.digest(lab.dump(hashes).encode())
    return "CDD Guardian package sha256:" + digest


def check_context(case, outputs, packet, evaluator):
    folder = HERE / case["id"]
    context = lab.read(folder / "context.json")
    inputs = lab.read(packet / "inputs.json")
    for key in ("task_ref", "base_sha", "code_sha", "corpus_hash"):
        check(context["inputs"][key], inputs[key], "operator context " + key)
    check(context["inputs"]["evaluator"], evaluator, "evaluator revision")
    measurements = {}
    for row in context["evidence"]:
        action = row["scope"]
        command = f"python3 reader.py {action} -> "
        if not row["observation"].startswith(command):
            raise ValueError(f"unexpected evidence command for {action}")
        measurements[action] = json.loads(row["observation"][len(command):])
    check(measurements, outputs, "observations in the independent context")
    verdict = lab.read(folder / "verdict.json")
    check((context["context_kind"], verdict["record_kind"]), ("example", "example"), "exercise provenance")
    checker = lab.ROOT / "skills/cdd-guardian/scripts/check_verdict.py"
    subprocess.run([sys.executable, "-B", str(checker), str(folder / "verdict.json"),
                    "--context", str(folder / "context.json")], check=True, stdout=subprocess.DEVNULL)
    for stage, key in (("pre", "initial_gate"), ("post", "final_gate")):
        archived = case["arms"]["guardian"]["stages"][stage]["response"]["gate"]
        check(verdict["dialogue"][key], archived, "Guardian dialogue " + stage)


def reference_blocks(outputs):
    blocks = []
    for action, observed in outputs.items():
        for clause, field, allowed in (("R-01", "marks_complete", "finish"),
                                       ("R-02", "suggestions_visible", "suggest")):
            if action != allowed and observed[field] is True:
                blocks.append({"clause": clause, "action": action, "field": field, "value": True})
        if action == "archive" and observed["archive_order"] != "newest":
            blocks.append({"clause": "A-01", "action": action,
                           "field": "archive_order", "value": observed["archive_order"]})
    return blocks


def replay(work):
    plan = lab.read(HERE / "plan.json")
    saved = lab.read(HERE / "results.json")
    check(lab.digest((HERE / "plan.json").read_bytes()), saved["plan_sha256"], "preregistered plan")
    tasks = {task["id"]: task for task in plan["cases"]}
    check([case["id"] for case in saved["cases"]], list(tasks), "planned case coverage")
    base = work / "base"
    restore_base(base, plan["base_source_commit"], saved["fixture_base"])
    baseline = {action: observe(base, action) for action in BASE_ACTIONS}
    cases, labels, captures = [], {}, {}
    for case in saved["cases"]:
        key = case["id"]
        task = tasks[key]
        candidate = work / key
        lab.git(work, "clone", "--quiet", "--local", str(base), str(candidate))
        lab.git(candidate, "apply", "--unidiff-zero", "--index", str(HERE / key / "change.patch"))
        install_commit(candidate, case["candidate"])
        captures[key] = {action: observe(candidate, action) for action in (*BASE_ACTIONS, task["action"])}
        for action, value in baseline.items():
            check(captures[key][action], value, f"{key} regression on {action}")
        if key == "resume":
            check(captures[key]["resume"], baseline["open"], "resume on default policy")
            check_configured_resume(candidate, saved["configured_resume_example"], work / "configured")
        observations = key + "-outputs.json"
        lab.write(work / observations, lab.dump(captures[key]))
        labels[key] = case["reference"]
        check(reference_blocks(captures[key]), labels[key]["blocks"], key + " registered witnesses")
        cases.append({"id": key, "family": task["family"], "split": "evaluation", "repo": key,
                      "code_sha": case["candidate"]["sha"], "base_sha": saved["fixture_base"]["sha"],
                      "acceptance_ref": "simulation-only", "sources": ["CANON.md", "ARCHIVE.md"],
                      "observations": observations, "task": task["ticket"], "defense": case["author_explanation"]})
    manifest = work / "manifest.json"
    lab.write(manifest, lab.dump({"cases": cases, "labels": labels, "label_provenance": saved["label_provenance"]}))
    run = work / "review"
    lab.prepare(run, seed=saved["seed"], split="evaluation", token_budget=saved["token_budget"], manifest=manifest)
    evaluator = evaluator_id(plan["base_source_commit"], run / "operator/skills/cdd-guardian")
    for case in saved["cases"]:
        trial = case["trial"]
        packet = run / "packets" / trial
        check(lab.tree_hash(packet), case["packet_sha256"], "locked evidence packet")
        check_context(case, captures[case["id"]], packet, evaluator)
        arms = case["arms"]
        lab.bind_author(run, trial, arms["lead-self"]["session_alias"], "Archived Lead handoff", case["candidate"]["sha"])
        for stage in ("pre", "post"):
            for arm in ARMS:
                session = arms[arm]["session_alias"]
                if stage == "post":
                    check(lab.defense(run, trial, arm, session), case["author_explanation"], "author statement")
                result = arms[arm]["stages"][stage]
                lab.enter(run, trial, arm, stage, session, saved["model"], result["response"],
                          tokens=result["tokens"], seconds=result["seconds"], human_minutes=result["human_minutes"])
    stats = lab.score(run)
    for arm in ARMS:
        check(stats["scores"][arm], saved["observed_scores"][arm], arm + " scores")
    check(stats["shared_miss"], saved["shared_miss"], "conditional shared miss")
    for row in sorted(stats["rows"], key=lambda row: (row["trial"], row["arm"], row["stage"] == "post")):
        print(f"{row['trial']} {row['arm']:9} {row['stage']:4} {row['gate']:5}  exact={row['exact']}")
    print(f"{stats['planned_trials']} candidate histories and example records verified; "
          f"{stats['observations']} archived observations rescored.")


if __name__ == "__main__":
    with tempfile.TemporaryDirectory() as tmp:
        replay(Path(tmp))
