"""Exercise the v0.4 decision contract on the fictional reading desk. Python 3.10+."""
import argparse
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import lab

CHECKER = lab.ROOT / "skills/cdd-guardian/scripts/check_verdict.py"
NEW_NORM = "- **R-06.** Readers may open a shared shelf from the library.\n"
REQUEST_ID = "shelf-policy"


def checker(*args):
    return subprocess.run([sys.executable, str(CHECKER), *map(str, args)], capture_output=True, text=True)


def commit(repo, message):
    lab.git(repo, "add", ".")
    lab.git(repo, "commit", "-qm", message)
    return lab.git(repo, "rev-parse", "HEAD")


def make_case(repo, dest, base, accepted=False, violation=False):
    lab.git(repo, "checkout", "-q", base)
    policy = lab.read(repo / "policy.json")
    policy["shared_shelf"] = True
    if violation:
        policy["auto_suggest"] = ["open"]
    lab.write(repo / "policy.json", lab.dump(policy))
    lab.write(repo / "RELEASE-NOTE.md", "A shared shelf is available from the library.\n")
    head = commit(repo, "Reading desk candidate")
    dest.mkdir()
    sources = dest / "base-sources"
    sources.mkdir()
    for file in ("CANON.md", "ARCHIVE.md"):
        (sources / file).write_bytes(subprocess.check_output(["git", "show", f"{base}:{file}"], cwd=repo))
    inputs = {"base_sha": base, "code_sha": head, "corpus_hash": lab.tree_hash(sources),
              "task_ref": "example:shared-shelf", "evaluator": "example:record-demo-v0.4"}
    evidence = []
    for surface in ("open", "library"):
        result = json.loads(subprocess.check_output([sys.executable, str(repo / "reader.py"), surface], text=True))
        evidence.append({"ref": f"reader/{surface}", "scope": surface,
                         "observation": f"python3 reader.py {surface} -> {json.dumps(result, sort_keys=True)}"})
        if surface == "open" and result["suggestions_visible"] != violation:
            raise RuntimeError("the captured opening behavior differs from the scenario")
        if surface == "library" and result["shared_shelf"] is not True:
            raise RuntimeError("the candidate did not expose the library shelf")
    revision = lab.digest(NEW_NORM.encode())
    decision = None
    clauses = [{"clause": "R-02", "scope": "open", "status": "VIOLATED" if violation else "PRESERVED",
                "required": True, "evidence_ref": "reader/open"}]
    findings = []
    if violation:
        findings.append({"severity": "BLOCK", "clause": "R-02", "scope": "open",
                         "cite": "R-02 in base-sources/CANON.md",
                         "counterexample": "open returns suggestions_visible=true without a request"})
    if accepted:
        decision = {"outcome": "ACCEPTED", "principal_id": "example:human-master",
                    "norm_revision": revision, "decision_ref": "example:simulated-human-event",
                    "base_sha": base, "corpus_hash": inputs["corpus_hash"]}
        clauses.append({"clause": "R-06", "scope": "library", "status": "PRESERVED", "required": True,
                        "evidence_ref": "reader/library"})
    context = {"context_kind": "example", "inputs": inputs, "human_masters": ["example:human-master"],
               "expected_scope": [{"scope": "open", "clauses": ["R-02"]},
                                  {"scope": "library", "clauses": ["R-06"] if accepted else []},
                                  {"scope": "release note", "clauses": [], "exclusion_ref": "example:docs-only"}],
               "evidence": evidence, "norm_requests": [{"request_id": REQUEST_ID, "scope": "library",
                                                        "follow_up_owner": "Lead", "norm_revision": revision,
                                                        "decision": decision}]}
    gate = "NO-GO" if violation else ("GO" if accepted else "HOLD")
    lab.write(dest / "context.json", lab.dump(context))
    hashed = checker("--hash-context", dest / "context.json")
    hashed.check_returncode()
    record = {"record_kind": "example", "protocol_version": "0.4",
              "inputs": {**inputs, "context_sha256": hashed.stdout.strip()},
              "scope": {"selection": [{"source": "CANON.md", "path": "policy.json", "rule": "load-full-example"}],
                        "unresolved": [], "exclusions": [{"scope": "release note", "basis_ref": "example:docs-only",
                                                          "reason": "This change to the note edits release copy only."}]},
              "clauses": clauses, "findings": findings,
              "routing": [] if accepted else [{"kind": "NEEDS-NORM", "scope": "library", "request_id": REQUEST_ID,
                                               "reason": "A shared shelf needs a product identity decision.",
                                               "follow_up_owner": "Lead", "decision_authority": "Master"}],
              "norm_decisions": [{**decision, "request_id": REQUEST_ID}] if accepted else [],
              "canon_gate": gate, "dialogue": {"initial_gate": gate, "final_gate": gate, "change_reason": None}}
    lab.write(dest / "verdict.json", lab.dump(record))
    verified = checker(dest / "verdict.json", "--context", dest / "context.json")
    if verified.returncode:
        raise RuntimeError(verified.stderr.strip())
    print(f"{dest.name}: {gate} (illustrative record checked)")


def reject(dest, record, context_path, expected_error):
    lab.write(dest, lab.dump(record))
    checked = checker(dest, "--context", context_path)
    if not checked.returncode or expected_error not in checked.stderr:
        raise RuntimeError(f"unexpected result for {dest.name}: {checked.stdout} {checked.stderr}")
    print(f"{dest.stem}: rejected ({expected_error})")


def demo(output):
    output.mkdir()
    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp)
        shutil.copytree(lab.HERE / "reader", repo, dirs_exist_ok=True, ignore=shutil.ignore_patterns("__pycache__"))
        lab.git(repo, "init", "-q")
        initial = commit(repo, "Original fictional reading desk")
        make_case(repo, output / "01-pending", initial)
        make_case(repo, output / "02-block-and-pending", initial, violation=True)
        lab.git(repo, "checkout", "-q", initial)
        with (repo / "CANON.md").open("a", encoding="utf-8") as f:
            f.write("\n" + NEW_NORM)
        revised = commit(repo, "Simulated new source revision")
        make_case(repo, output / "03-reassessed", revised, accepted=True)
    reviewed = output / "03-reassessed"
    valid = lab.read(reviewed / "verdict.json")
    omitted = copy.deepcopy(valid)
    omitted["clauses"].pop()
    reject(reviewed / "invalid-missing-scope.json", omitted, reviewed / "context.json", "missing required assessment")
    substitute = copy.deepcopy(valid)
    substitute["norm_decisions"][0]["principal_id"] = "Lead"
    reject(reviewed / "invalid-tracker-approval.json", substitute, reviewed / "context.json", "matching independent decision")
    reject(reviewed / "invalid-stale-record.json", lab.read(output / "01-pending/verdict.json"),
           reviewed / "context.json", "inputs differ")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, help="retain the packets in a new directory")
    args = parser.parse_args()
    if args.out is not None and args.out.exists():
        parser.error("--out needs a new directory")
    with tempfile.TemporaryDirectory(dir=args.out.parent if args.out else None) as tmp:
        result = Path(tmp) / "packets"
        demo(result)
        if args.out:
            result.rename(args.out)


if __name__ == "__main__":
    main()
