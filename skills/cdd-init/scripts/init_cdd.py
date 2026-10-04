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
            raise ValueError(f"Hedef yol symlink içeriyor: {part}")
    if target.exists() and not target.is_dir():
        raise ValueError("Hedef bir dizin olmalı")
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
        raise ValueError("Hiçbir dosya yazılmadı; çakışan yollar: " + ", ".join(conflicts))
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
                        help="Mevcut AGENTS.md için otomatik yazımı atla; elle uzlaştırma gerekir")
    args = parser.parse_args()
    try:
        planned, unchanged = initialize(args.target, args.dry_run, args.skip_agents)
    except (OSError, ValueError) as exc:
        print(f"CDD init: {exc}", file=sys.stderr)
        return 1
    print("Planlanan:" if args.dry_run else "Oluşturulan:", ", ".join(planned) or "yok")
    print("Aynı kalan:", ", ".join(unchanged) or "yok")
    print("Canon DRAFT'tır; bu işlem norm kabulü, çalışan ajan veya CI gate kurmaz.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
