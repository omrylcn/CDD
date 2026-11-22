import copy
import importlib.util
import json
import shutil
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("phase0_lab", ROOT / "experiments/phase0/lab.py")
lab = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lab)


class LabTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.template = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.template.cleanup)
        cls.frozen = Path(cls.template.name) / "run"
        lab.prepare(cls.frozen)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.run = self.root / "run"
        shutil.copytree(self.frozen, self.run)
        self.trials = {m["case"]: t for t, m in lab.read_plan(self.run)["trials"].items()}

    def response(self, case):
        trial = self.trials[case]
        return dict(lab.plan_trial(self.run, trial)[1]["gold"], reason="Checked the public result.")

    def submit(self, case, arm, stage, session, result=None, model="local", **usage):
        result = self.response(case) if result is None else result
        lab.enter(self.run, self.trials[case], arm, stage, session, model, result, **usage)

    def test_sources_are_loaded_at_base_and_candidate_cannot_redefine_them(self):
        folder = self.run / "packets" / self.trials["11"]
        self.assertIn("Opening an entry may mark it complete", (folder / "change.diff").read_text())
        self.assertIn("only when the reader explicitly finishes", (folder / "base-sources/CANON.md").read_text())
        self.assertTrue(lab.read(folder / "observations.json")["open"]["marks_complete"])

    def test_neutral_and_pressure_packets_are_identical_before_the_defense(self):
        _, a = lab.plan_trial(self.run, self.trials["02"])
        _, b = lab.plan_trial(self.run, self.trials["03"])
        self.assertEqual(a["digest"], b["digest"])
        self.assertNotEqual(a["defense"], b["defense"])
        self.assertEqual(a["split"], b["split"])

    def test_export_hides_labels_and_refuses_to_reuse_a_directory(self):
        path = self.root / "editor"
        lab.export(self.run, self.trials["07"], "guardian", path)
        self.assertFalse((path / "gold.json").exists())
        self.assertTrue((path / ".claude/agents/cdd-guardian.md").is_file())
        self.assertFalse((path / "base-sources/ARCHIVE.md").exists())
        self.assertEqual(lab.read(path / "inputs.json")["missing_sources"], ["ARCHIVE.md"])
        with self.assertRaises(ValueError):
            lab.export(self.run, self.trials["07"], "baseline", path)

    def test_frozen_packets_and_labels_detect_edits(self):
        trial = self.trials["01"]
        (self.run / "packets" / trial / "task.md").write_text("Different task")
        with self.assertRaises(ValueError):
            lab.export(self.run, trial, "baseline", self.root / "edited")
        with (self.run / "operator/plan.json").open("a") as f:
            f.write("\n")
        with self.assertRaises(ValueError):
            lab.score(self.run)

    def test_pre_is_immutable_and_the_same_guardian_continues(self):
        trial = self.trials["07"]
        with self.assertRaises(ValueError):
            lab.defense(self.run, trial, "guardian", "A")
        self.submit("07", "guardian", "pre", "A")
        with self.assertRaises(sqlite3.IntegrityError):
            self.submit("07", "guardian", "pre", "A")
        for arm, stage, session, model in [("guardian", "post", "B", "local"),
                                            ("guardian", "post", "A", "other"),
                                            ("baseline", "pre", "A", "local")]:
            with self.assertRaises(ValueError):
                self.submit("07", arm, stage, session, model=model)
        self.assertIn("later", lab.defense(self.run, trial, "guardian", "A"))
        self.submit("07", "guardian", "post", "A")
        lab.audit_packet(self.run, trial, self.root / "handoff")
        records = lab.read(self.root / "handoff/decision-trail.json")["records"]
        self.assertEqual([r["stage"] for r in records], ["pre", "post"])

    def test_wrong_evidence_and_a_dropped_route_are_detected_separately(self):
        good = self.response("07")
        wrong = copy.deepcopy(good)
        wrong["blocks"][0]["value"] = 1
        self.submit("07", "baseline", "pre", "A", wrong)
        self.submit("07", "guardian", "pre", "B", dict(good, routes=[]))
        result = lab.score(self.run)["scores"]
        self.assertEqual(result["baseline"]["pre"]["wrong_evidence_on_violations"], 1)
        self.assertEqual(result["baseline"]["pre"]["recall"]["n"], 0)
        self.assertEqual(result["guardian"]["pre"]["recall"]["n"], 1)
        self.assertEqual(result["guardian"]["pre"]["exact"]["n"], 0)

    def test_shared_miss_requires_author_binding_and_matched_guardian(self):
        trial = self.trials["07"]
        head = lab.read(self.run / "packets" / trial / "inputs.json")["code_sha"]
        with self.assertRaises(ValueError):
            self.submit("07", "lead-self", "pre", "writer")
        lab.bind_author(self.run, trial, "writer", "synthetic test provenance", head)
        with self.assertRaises(ValueError):
            self.submit("07", "guardian", "pre", "writer")
        self.submit("07", "lead-self", "pre", "writer", self.response("01"))
        self.assertIsNone(lab.score(self.run)["shared_miss"]["pre"]["rate"])
        self.submit("07", "guardian", "pre", "reviewer", self.response("01"))
        self.submit("07", "guardian", "post", "reviewer", self.response("07"))
        result = lab.score(self.run)["shared_miss"]
        self.assertEqual(result["pre"]["rate"], 1)
        self.assertEqual(result["post"]["rate"], 0)
        self.assertEqual(result["post"]["of"], 1)

    def test_missing_costs_and_zero_denominators_stay_unknown(self):
        self.submit("06", "guardian", "pre", "A", tokens=5000, seconds=1)
        self.submit("06", "guardian", "post", "A", tokens=4000)
        result = lab.score(self.run)
        self.assertTrue(result["usage"][0]["over_token_budget"])
        self.assertIsNone(result["usage"][0]["seconds"])
        self.assertIsNone(result["shared_miss"]["pre"]["rate"])
        self.assertIsNone(result["scores"]["guardian"]["pre"]["false_block"]["rate"])
        self.assertEqual(result["scores"]["guardian"]["pre"]["hold"]["rate"], 1)

    def test_external_manifest_uses_real_base_source_and_external_observations(self):
        repo = self.root / "product"
        repo.mkdir()
        lab.git(repo, "init", "-q")
        (repo / "CANON.md").write_text("Active rule\n")
        (repo / "policy.txt").write_text("base\n")
        lab.git(repo, "add", ".")
        lab.git(repo, "commit", "-qm", "Base")
        base = lab.git(repo, "rev-parse", "HEAD")
        (repo / "CANON.md").write_text("Candidate proposal\n")
        lab.git(repo, "add", ".")
        lab.git(repo, "commit", "-qm", "Change")
        head = lab.git(repo, "rev-parse", "HEAD")
        (self.root / "observations.json").write_text('{"open":{"value":true}}')
        case = {"id": "x", "family": "surface", "split": "evaluation", "repo": "product",
                "base_sha": base, "code_sha": head, "sources": ["CANON.md"],
                "observations": "observations.json", "task": "Review the proposed change.",
                "defense": "No new information.", "acceptance_ref": "illustrative test reference"}
        data = {"cases": [case], "labels": {"x": self.response("01")}, "label_provenance": "test fixture"}
        path = self.root / "manifest.json"
        path.write_text(json.dumps(data))
        run = self.root / "external"
        lab.prepare(run, manifest=path)
        packet = run / "packets/t001"
        self.assertEqual((packet / "base-sources/CANON.md").read_text(), "Active rule\n")
        self.assertIn("Candidate proposal", (packet / "change.diff").read_text())
        self.assertEqual(lab.read(packet / "inputs.json")["code_sha"], head)
        case["sources"] = ["../outside"]
        path.write_text(json.dumps(data))
        with self.assertRaises(ValueError):
            lab.prepare(self.root / "bad", manifest=path)
        self.assertFalse((self.root / "bad").exists())

    def test_local_plugin_contains_three_roles_and_canonical_skill_files(self):
        dest = self.root / "plugin"
        lab.package_plugin(dest)
        self.assertEqual(lab.read(dest / ".claude-plugin/plugin.json")["name"], "cdd-phase0")
        self.assertEqual(len(list((dest / "agents").glob("*.md"))), 3)
        for name in ("cdd-init", "cdd-guardian", "cdd-inspect"):
            self.assertEqual((ROOT / "skills" / name / "SKILL.md").read_bytes(),
                             (dest / "skills" / name / "SKILL.md").read_bytes())

    def test_archived_observations_replay_on_the_frozen_packets(self):
        score = lab.replay_sample()
        self.assertEqual(score["observations"], 8)
        self.assertEqual(score["scores"]["guardian"]["post"]["coverage"]["n"], 2)
        self.assertEqual(score["scores"]["baseline"]["post"]["exact"]["n"], 2)
        self.assertIsNone(score["shared_miss"]["post"]["rate"])
