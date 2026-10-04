#!/usr/bin/env python3
"""Check a CDD record contract, not the truth of the review or approval identity."""
import argparse
import json
from pathlib import Path
import re
import sys

STATES = {"PRESERVED", "VIOLATED", "AMBIGUOUS", "NOT_ASSESSED"}
ROUTES = {"NEEDS-RULING", "NEEDS-NORM", "CONTEXT", "INSTABILITY"}
GATES = {"GO", "NO-GO", "HOLD"}

def member(value, choices):
    return isinstance(value, str) and value in choices

def validate(record):
    errors=[]
    if not isinstance(record, dict):
        return ["record must be an object"]
    kind=record.get("record_kind")
    if not member(kind, {"template", "example", "review"}):
        errors.append("record_kind must be template, example or review")
    if record.get("protocol_version") != "0.3":
        errors.append("protocol_version must be 0.3")
    inputs=record.get("inputs")
    if not isinstance(inputs,dict):
        errors.append("inputs must be an object"); inputs={}
    required_inputs={"code_sha","base_sha","corpus_hash","task_ref","evaluator"}
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
        if f.get("severity")=="ADVISORY" and not all(f.get(k) for k in ("owner","review_date")):
            errors.append("ADVISORY requires owner and review_date")
    for key,status in seen.items():
        if status=="VIOLATED" and key not in block_keys: errors.append("VIOLATED requires matching BLOCK evidence")
    for route in routing:
        if not isinstance(route,dict) or not member(route.get("kind"), ROUTES) or not route.get("reason") or not route.get("owner"):
            errors.append("route requires known kind, reason and owner"); continue
        if route["kind"]=="NEEDS-RULING" and not route.get("cite"):
            errors.append("NEEDS-RULING requires a cite")
    if not scope["unresolved"] and not scope["selection"]:
        errors.append("resolved scope needs a recorded selection")
    expected="NO-GO" if block_keys else "HOLD" if routing or scope["unresolved"] or incomplete else "GO"
    if not member(record.get("canon_gate"), GATES) or record.get("canon_gate")!=expected:
        errors.append(f"canon_gate must be {expected} for the recorded fields")
    if kind=="template" and record.get("canon_gate")!="HOLD": errors.append("template cannot be a completed review")
    return errors

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("record")
    args=parser.parse_args()
    try:
        record=json.loads(Path(args.record).read_text())
        errors=validate(record)
    except (OSError,ValueError) as exc:
        errors=[str(exc)]
    if errors:
        print("\n".join(errors),file=sys.stderr); return 1
    print("Record contract is consistent. Semantic correctness, human approval, and gate passage were not verified.")
    return 0

if __name__=="__main__":
    raise SystemExit(main())
