#!/usr/bin/env python3
"""Create CDD Phase 0 drafts; never approve norms or overwrite existing files."""
import argparse
from pathlib import Path
import sys

TEMPLATES = Path(__file__).resolve().parents[1] / "assets" / "templates"

def initialize(target, dry_run=False, skip_agents=False):
    target = Path(target).absolute()
    # Refuse symlink traversal before computing or creating output paths.
    for part in (target, *target.parents):
        if part.is_symlink():
            raise ValueError(f"Target path contains a symlink: {part}")
    if target.exists() and not target.is_dir():
        raise ValueError("Target must be a directory")
    plan, unchanged, conflicts = [], [], []
    for src in sorted(TEMPLATES.rglob("*")):
        if not src.is_file():
            continue
        rel = src.relative_to(TEMPLATES)
        if skip_agents and rel.as_posix() == "AGENTS.md":
            continue
        dst = target / rel
        parent_conflict = any(p.is_symlink() or (p.exists() and not p.is_dir())
                              for p in dst.parents if p != target.parent)
        if dst.is_symlink() or parent_conflict:
            conflicts.append(str(rel))
        elif dst.exists():
            if dst.is_file() and dst.read_bytes() == src.read_bytes():
                unchanged.append(str(rel))
            else:
                conflicts.append(str(rel))
        else:
            plan.append((src, dst))
    if conflicts:
        raise ValueError("No files written; conflicting paths: " + ", ".join(conflicts))
    created = []
    if not dry_run:
        try:
            for src, dst in plan:
                dst.parent.mkdir(parents=True, exist_ok=True)
                # Exclusive creation also guards a file created after preflight.
                with dst.open("xb") as handle:
                    created.append(dst)
                    handle.write(src.read_bytes())
        except Exception:
            for dst in created:
                dst.unlink(missing_ok=True)
            raise
    return [str(dst.relative_to(target)) for _, dst in plan], unchanged

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--skip-agents", action="store_true",
                        help="Skip writing AGENTS.md; manual reconciliation is required")
    args = parser.parse_args()
    try:
        planned, unchanged = initialize(args.target, args.dry_run, args.skip_agents)
    except (OSError, ValueError) as exc:
        print(f"CDD init: {exc}", file=sys.stderr)
        return 1
    print("Planned:" if args.dry_run else "Created:", ", ".join(planned) or "none")
    print("Unchanged:", ", ".join(unchanged) or "none")
    print("Canon remains DRAFT; this does not accept norms, run agents, or configure a CI gate.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
