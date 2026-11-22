"""Tiny reading desk used to exercise observable product behavior."""
import argparse
import json
from pathlib import Path

ACTIONS = ("open", "preview", "finish", "suggest", "library", "archive")


def observe(policy, action):
    if action not in ACTIONS:
        raise ValueError(f"unknown action: {action}")
    return {
        "marks_complete": action == "finish" or action in policy["auto_finish"],
        "suggestions_visible": action == "suggest" or action in policy["auto_suggest"],
        "caption": policy["caption"],
        "library_link": action == "open" and policy["library_link"],
        "shared_shelf": action == "library" and policy["shared_shelf"],
        "archive_order": policy["archive_order"] if action == "archive" else None,
        "information_labels": policy["information_labels"] if action == "open" else [],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=ACTIONS)
    args = parser.parse_args()
    policy = json.loads(Path(__file__).with_name("policy.json").read_text(encoding="utf-8"))
    print(json.dumps(observe(policy, args.action), sort_keys=True))
