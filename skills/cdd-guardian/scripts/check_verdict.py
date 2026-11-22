#!/usr/bin/env python3
"""Check a CDD record contract, not the truth of the review or approval identity."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

STATES = {"PRESERVED", "VIOLATED", "AMBIGUOUS", "NOT_ASSESSED"}
ROUTES = {"NEEDS-RULING", "NEEDS-NORM", "CONTEXT", "INSTABILITY"}
GATES = {"GO", "NO-GO", "HOLD"}
INPUT_KEYS = ("code_sha", "base_sha", "corpus_hash", "task_ref", "evaluator")
AUTHORITIES = {"NEEDS-NORM": "Master", "NEEDS-RULING": "Council", "INSTABILITY": "Master",
               "CONTEXT": None}

def member(value, choices):
    return isinstance(value, str) and value in choices

def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def sha256_id(value):
    return isinstance(value, str) and re.fullmatch(r"[0-9a-f]{64}", value) is not None


def context_digest(context):
    encoded = json.dumps(context, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
                         allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def indexed(rows, field, label, errors):
    result = {}
    if not isinstance(rows, list):
        errors.append(f"{label} must be a list")
        return result
    for row in rows:
        if not isinstance(row, dict) or not nonempty(row.get(field)):
            errors.append(f"{label} requires a nonempty {field}")
            continue
        key = row[field]
        if key in result:
            errors.append(f"duplicate {field} in {label}: {key}")
        result[key] = row
    return result


def string_list(values):
    return (isinstance(values, list) and all(nonempty(v) for v in values)
            and len(values) == len(set(values)))


def check_coverage(context, scope, clauses, routes, errors):
    expected = indexed(context.get("expected_scope"), "scope", "expected_scope", errors)
    exclusions = indexed(scope.get("exclusions"), "scope", "scope.exclusions", errors)
    evidence = indexed(context.get("evidence"), "ref", "context.evidence", errors)
    for selection in scope["selection"]:
        if not isinstance(selection, dict) or not all(nonempty(selection.get(k)) for k in ("path", "rule", "source")):
            errors.append("each selection needs a path, rule and source")
    for ref, entry in evidence.items():
        if not nonempty(entry.get("scope")) or not nonempty(entry.get("observation")):
            errors.append(f"{ref} needs a scope and a captured observation")
    assessed = {}
    for row in clauses:
        if not isinstance(row, dict) or not all(nonempty(row.get(k)) for k in ("clause", "scope")):
            errors.append("assessment needs a nonempty clause and scope")
            continue
        surface = row["scope"]
        assessed.setdefault(surface, {})[row["clause"]] = row
        if member(row.get("status"), {"PRESERVED", "VIOLATED"}):
            ref = row.get("evidence_ref")
            if not nonempty(ref) or evidence.get(ref, {}).get("scope") != surface:
                errors.append(f"{row['clause']} on {surface} needs evidence captured for that scope")
    for surface, row in exclusions.items():
        basis = row.get("basis_ref")
        if (not nonempty(row.get("reason")) or not nonempty(basis)
                or expected.get(surface, {}).get("exclusion_ref") != basis):
            errors.append(f"unsupported exclusion: {surface}")
        if surface in assessed:
            errors.append(f"scope cannot be both excluded and assessed: {surface}")
    open_scopes = {r["scope"] for r in routes if isinstance(r, dict) and nonempty(r.get("scope"))}
    if not expected and not any(isinstance(r, dict) and r.get("kind") == "CONTEXT" for r in routes):
        errors.append("empty expected scope requires open CONTEXT routing")
    for surface, row in expected.items():
        required = row.get("clauses")
        if not string_list(required):
            errors.append(f"expected clauses for {surface} must be unique nonempty identifiers")
            continue
        if surface in exclusions:
            continue
        actual = assessed.get(surface, {})
        for clause in required:
            if actual.get(clause, {}).get("required") is not True:
                errors.append(f"missing required assessment: {clause} on {surface}")
        if not required and surface not in open_scopes and not any(c.get("required") is True for c in actual.values()):
            errors.append(f"scope needs an assessment, authorized exclusion or open route: {surface}")


def check_norms(context, decisions, routes, errors):
    masters = context.get("human_masters")
    if not string_list(masters):
        errors.append("human_masters must list unique human principal IDs from the trusted source")
        masters = []
    requests = indexed(context.get("norm_requests"), "request_id", "context.norm_requests", errors)
    recorded = indexed(decisions, "request_id", "norm_decisions", errors)
    pending = {}
    for route in routes:
        if not isinstance(route, dict) or not member(route.get("kind"), ROUTES):
            continue
        kind = route["kind"]
        if not all(nonempty(route.get(k)) for k in ("scope", "follow_up_owner", "reason")):
            errors.append(f"{kind} needs a scope, follow_up_owner and reason")
        if "decision_authority" not in route or route["decision_authority"] != AUTHORITIES[kind]:
            errors.append(f"{kind} requires decision_authority={AUTHORITIES[kind]}")
        allowed = {"kind", "scope", "reason", "follow_up_owner", "decision_authority"}
        if kind == "NEEDS-NORM":
            allowed.add("request_id")
            request = route.get("request_id")
            if not nonempty(request) or request in pending:
                errors.append("NEEDS-NORM requires a unique request_id")
            else:
                pending[request] = (route.get("scope"), route.get("follow_up_owner"))
        if kind == "NEEDS-RULING":
            allowed.add("cite")
            if not nonempty(route.get("cite")):
                errors.append("NEEDS-RULING needs a textual citation")
        if route.keys() - allowed:
            errors.append(f"{kind} contains unsupported route fields; use norm_decisions for decisions")
    for key in recorded.keys() - requests.keys():
        errors.append(f"no independent norm request for decision: {key}")
    for key, request in requests.items():
        scope = request.get("scope")
        owner = request.get("follow_up_owner")
        revision = request.get("norm_revision")
        if (not nonempty(scope) or not nonempty(owner) or "norm_revision" not in request
                or (revision is not None and not sha256_id(revision))):
            errors.append(f"invalid scope, follow-up owner or norm revision for {key}")
        if "decision" not in request:
            errors.append(f"{key} must declare a decision or explicit null")
        decision = request.get("decision")
        if decision is None:
            if key in recorded or pending.get(key) != (scope, owner):
                errors.append(f"{key} must remain open on the registered scope with the assigned follow-up owner")
            continue
        if not isinstance(decision, dict):
            errors.append(f"invalid trusted decision for {key}")
            continue
        for field in ("outcome", "principal_id", "norm_revision", "decision_ref", "base_sha", "corpus_hash"):
            if not nonempty(decision.get(field)):
                errors.append(f"decision for {key} needs {field}")
        if not member(decision.get("outcome"), {"ACCEPTED", "DECLINED"}):
            errors.append(f"invalid outcome for {key}")
        if decision.get("principal_id") not in masters:
            errors.append(f"decision for {key} requires an independently identified human Master")
        if not sha256_id(revision) or decision.get("norm_revision") != revision:
            errors.append(f"decision for {key} does not bind the proposed norm bytes")
        if any(decision.get(k) != context["inputs"].get(k) for k in ("base_sha", "corpus_hash")):
            errors.append(f"decision for {key} does not apply to the reviewed base and corpus")
        if key in pending or recorded.get(key) != {**decision, "request_id": key}:
            errors.append(f"{key} needs a matching independent decision and cannot remain in open routing")


def validate_v04(record, context, scope, inputs, clauses, routes):
    errors = []
    if record.get("record_kind") == "template":
        if (context is not None or record.get("norm_decisions") != [] or scope.get("exclusions") != []
                or not any(isinstance(r, dict) and r.get("kind") == "CONTEXT" for r in routes)):
            errors.append("v0.4 template requires open CONTEXT, empty decisions/exclusions and no trusted context")
        return errors
    if not isinstance(context, dict) or context.get("context_kind") != record.get("record_kind"):
        return ["v0.4 requires a separately supplied context matching the record kind"]
    trusted = context.get("inputs")
    if not isinstance(trusted, dict) or not all(nonempty(trusted.get(k)) for k in INPUT_KEYS):
        return ["incomplete independent context inputs"]
    if any(inputs.get(k) != trusted[k] for k in INPUT_KEYS):
        errors.append("record inputs differ from the independent context")
    if not sha256_id(trusted["corpus_hash"]):
        errors.append("v0.4 corpus_hash must be a SHA-256 digest")
    if inputs.get("context_sha256") != context_digest(context):
        errors.append("context_sha256 does not match the supplied context")
    check_coverage(context, scope, clauses, routes, errors)
    check_norms(context, record.get("norm_decisions"), routes, errors)
    return errors


def validate(record, context=None, require_review=False):
    errors=[]
    if not isinstance(record, dict):
        return ["record must be an object"]
    kind=record.get("record_kind")
    if not member(kind, {"template", "example", "review"}):
        errors.append("record_kind must be template, example or review")
    version = record.get("protocol_version")
    if not member(version, {"0.3", "0.4"}):
        errors.append("unsupported protocol_version")
    if require_review and (kind != "review" or version != "0.4"):
        errors.append("expected a v0.4 review record")
    if version != "0.4" and context is not None:
        errors.append("a trusted context requires v0.4")
    inputs=record.get("inputs")
    if not isinstance(inputs,dict):
        errors.append("inputs must be an object"); inputs={}
    required_inputs=set(INPUT_KEYS)
    if not required_inputs <= inputs.keys():
        errors.append("inputs are incomplete")
    if kind == "review":
        for key in required_inputs:
            if not isinstance(inputs.get(key),str) or not inputs[key].strip():
                errors.append(f"review input missing: {key}")
        for key in ("code_sha","base_sha"):
            if not isinstance(inputs.get(key),str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}",inputs[key]):
                errors.append(f"{key} must be a full commit hash")
    scope=record.get("scope")
    if not isinstance(scope,dict) or not isinstance(scope.get("selection"),list) or not isinstance(scope.get("unresolved"),list):
        errors.append("scope requires selection and unresolved lists"); scope={"selection":[],"unresolved":["invalid"]}
    for name in ("clauses","findings","routing"):
        if not isinstance(record.get(name),list):
            errors.append(f"{name} must be a list")
    clauses=record.get("clauses") if isinstance(record.get("clauses"),list) else []
    findings=record.get("findings") if isinstance(record.get("findings"),list) else []
    routing=record.get("routing") if isinstance(record.get("routing"),list) else []
    seen={}; incomplete=False
    for c in clauses:
        if not isinstance(c,dict) or not isinstance(c.get("clause"),str) or not isinstance(c.get("scope"),str):
            errors.append("clause entry requires clause and scope strings"); continue
        key=(c["clause"],c["scope"])
        if key in seen: errors.append(f"duplicate clause/scope: {key}")
        seen[key]=c.get("status")
        if not member(c.get("status"), STATES): errors.append(f"invalid clause state: {key}")
        if not isinstance(c.get("required"),bool): errors.append("clause required must be boolean")
        if c.get("required",True) and member(c.get("status"), {"AMBIGUOUS","NOT_ASSESSED"}): incomplete=True
    block_keys=set()
    for f in findings:
        if not isinstance(f,dict): errors.append("finding must be an object"); continue
        if not member(f.get("severity"), {"BLOCK","ADVISORY","OBSERVATION"}): errors.append("invalid finding severity")
        if f.get("severity")=="BLOCK":
            if not all(isinstance(f.get(k),str) and f[k].strip() for k in ("clause","scope","cite","counterexample")):
                errors.append("BLOCK requires clause, scope, cite and counterexample"); continue
            key=(f["clause"],f["scope"]); block_keys.add(key)
            if seen.get(key)!="VIOLATED": errors.append("BLOCK must match a VIOLATED clause/scope")
        if f.get("severity") == "ADVISORY":
            required = ("clause", "scope", "observation", "owner", "review_date")
            if not all(isinstance(f.get(k), str) and f[k].strip() for k in required):
                errors.append("ADVISORY requires clause, scope, observation, owner and review_date")
    for key,status in seen.items():
        if status=="VIOLATED" and key not in block_keys: errors.append("VIOLATED requires matching BLOCK evidence")
    owner_field = "follow_up_owner" if version == "0.4" else "owner"
    for route in routing:
        if not isinstance(route,dict) or not member(route.get("kind"), ROUTES) or not route.get("reason") or not route.get(owner_field):
            errors.append(f"route requires known kind, reason and {owner_field}"); continue
        if route["kind"]=="NEEDS-RULING" and not route.get("cite"):
            errors.append("NEEDS-RULING requires a cite")
    if not scope["unresolved"] and not scope["selection"]:
        errors.append("resolved scope needs a recorded selection")
    expected="NO-GO" if block_keys else "HOLD" if routing or scope["unresolved"] or incomplete else "GO"
    if not member(record.get("canon_gate"), GATES) or record.get("canon_gate")!=expected:
        errors.append(f"canon_gate must be {expected} for the recorded fields")
    if "dialogue" in record:
        dialogue = record["dialogue"]
        if not isinstance(dialogue, dict) or dialogue.get("final_gate") != record.get("canon_gate"):
            errors.append("dialogue.final_gate must match canon_gate")
    if kind=="template" and record.get("canon_gate")!="HOLD": errors.append("template cannot be a completed review")
    if version == "0.4":
        errors.extend(validate_v04(record, context, scope, inputs, clauses, routing))
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record", nargs="?")
    parser.add_argument("--context", help="independently obtained context for a v0.4 decision")
    parser.add_argument("--require-review", action="store_true", help="accept only v0.4 review-kind records")
    parser.add_argument("--hash-context", metavar="FILE", help="print the canonical context digest and exit")
    args=parser.parse_args()
    try:
        if args.hash_context:
            if args.record or args.context or args.require_review:
                parser.error("--hash-context takes only its file")
            print(context_digest(json.loads(Path(args.hash_context).read_text(encoding="utf-8"))))
            return 0
        if not args.record:
            parser.error("a verdict file is required")
        record=json.loads(Path(args.record).read_text(encoding="utf-8"))
        context = json.loads(Path(args.context).read_text(encoding="utf-8")) if args.context else None
        errors=validate(record, context, args.require_review)
    except (OSError,ValueError) as exc:
        errors=[str(exc)]
    if errors:
        print("\n".join(errors),file=sys.stderr); return 1
    if record.get("protocol_version") == "0.4":
        print(f"Consistent v0.4 {record['record_kind']} record. CANON_GATE={record['canon_gate']}. "
              "Verify source authenticity and semantic correctness independently.")
    else:
        print("Record contract is consistent. Semantic correctness, human approval, and gate passage were not verified.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
