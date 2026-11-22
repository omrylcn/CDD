import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_starter import CHECK, ROOT


class DraftRecordTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(temp.cleanup)
        cls.work = Path(temp.name)
        cls.packets = cls.work / "examples"
        cls.demo = subprocess.run(
            [sys.executable, "-B", str(ROOT / "experiments/phase0/record_demo.py"), "--out", str(cls.packets)],
            check=True, text=True, capture_output=True)
        cls.cli = ROOT / "skills/cdd-guardian/scripts/check_verdict.py"

    def packet(self, name="03-reassessed"):
        folder = self.packets / name
        return tuple(json.loads((folder / f"{file}.json").read_text(encoding="utf-8"))
                     for file in ("verdict", "context"))

    def rebind(self, record, context):
        # Isolate the semantic check from context-digest mismatch in these synthetic probes.
        record["inputs"]["context_sha256"] = CHECK.context_digest(context)
        return CHECK.validate(record, context)

    def test_demo_exercises_the_reader_and_the_normal_checker(self):
        self.assertEqual(self.demo.stdout.count("illustrative record checked"), 3)
        self.assertEqual(self.demo.stdout.count("rejected"), 3)
        for case, gate in (("01-pending", "HOLD"), ("02-block-and-pending", "NO-GO"), ("03-reassessed", "GO")):
            record, context = self.packet(case)
            self.assertEqual(record["canon_gate"], gate)
            self.assertEqual(CHECK.validate(record, context), [])
            self.assertIn("suggestions_visible", context["evidence"][0]["observation"])
        before, _ = self.packet("01-pending")
        after, _ = self.packet()
        self.assertNotEqual(before["inputs"]["base_sha"], after["inputs"]["base_sha"])
        self.assertNotEqual(before["inputs"]["corpus_hash"], after["inputs"]["corpus_hash"])

    def test_published_example_pair_can_be_checked_through_the_cli(self):
        pair = ROOT / "examples/reading-desk/v0.4"
        checked = subprocess.run([sys.executable, str(self.cli), str(pair / "verdict.json"), "--context",
                                  str(pair / "context.json")], check=True, capture_output=True, text=True)
        self.assertIn("example record. CANON_GATE=GO", checked.stdout)

    def test_missing_row_or_downgraded_required_flag_fails(self):
        for operation in ("omit one surface", "omit everything", "optionalize"):
            with self.subTest(operation=operation):
                record, context = self.packet()
                if operation == "omit one surface":
                    record["clauses"].pop()
                elif operation == "omit everything":
                    record["clauses"] = []
                else:
                    record["clauses"][-1]["required"] = False
                self.assertTrue(CHECK.validate(record, context))

    def test_evidence_must_exist_and_belong_to_the_surface(self):
        for ref in (None, "invented", "reader/open"):
            with self.subTest(ref=ref):
                record, context = self.packet()
                record["clauses"][-1]["evidence_ref"] = ref
                self.assertTrue(CHECK.validate(record, context))

    def test_exclusions_can_cover_every_surface_with_independent_basis(self):
        record, context = self.packet()
        expected = context["expected_scope"]
        record["clauses"] = []
        record["scope"]["exclusions"] = []
        for i, row in enumerate(expected):
            row["exclusion_ref"] = f"example:approved-exclusion-{i}"
            record["scope"]["exclusions"].append({"scope": row["scope"], "reason": "Teaching scope exemption.",
                                                 "basis_ref": row["exclusion_ref"]})
        self.assertEqual(self.rebind(record, context), [])
        record["scope"]["exclusions"][0]["basis_ref"] = "candidate-only"
        self.assertTrue(CHECK.validate(record, context))
        record["scope"]["exclusions"][0]["basis_ref"] = expected[0]["exclusion_ref"]
        record["scope"]["exclusions"][0]["reason"] = " "
        self.assertTrue(CHECK.validate(record, context))

    def test_empty_inventory_needs_context_and_keeps_an_independent_block(self):
        record, context = self.packet("02-block-and-pending")
        context["expected_scope"] = []
        record["scope"]["exclusions"] = []
        self.assertTrue(self.rebind(record, context))
        record["routing"].append({"kind": "CONTEXT", "scope": "inventory", "reason": "Await scope map.",
                                  "decision_authority": None, "follow_up_owner": "operator"})
        self.assertEqual(CHECK.validate(record, context), [])
        self.assertEqual(record["canon_gate"], "NO-GO")

    def test_not_assessed_is_recordable_without_claiming_evidence(self):
        record, context = self.packet()
        unreviewed = record["clauses"][0]
        unreviewed["status"] = "NOT_ASSESSED"
        del unreviewed["evidence_ref"]
        record["routing"] = [{"kind": "CONTEXT", "scope": unreviewed["scope"], "reason": "Run unavailable.",
                              "decision_authority": None, "follow_up_owner": "operator"}]
        self.assertTrue(CHECK.validate(record, context))
        record["canon_gate"] = record["dialogue"]["final_gate"] = "HOLD"
        self.assertEqual(CHECK.validate(record, context), [])

    def test_tracker_can_be_lead_but_new_norm_goes_to_master(self):
        record, context = self.packet("01-pending")
        self.assertEqual(record["routing"][0]["follow_up_owner"], "Lead")
        self.assertEqual(CHECK.validate(record, context), [])
        for patch in ({"decision_authority": "Lead"}, {"follow_up_owner": "unassigned substitute"},
                      {"owner": "Master"}, {"status": "ACCEPTED"},
                      {"decision_ref": "self-reported"}, {"request_id": "replacement"}):
            with self.subTest(patch=patch):
                changed = copy.deepcopy(record)
                changed["routing"][0].update(patch)
                self.assertTrue(CHECK.validate(changed, context))

    def test_deleting_pending_question_does_not_clear_it_even_if_another_block_exists(self):
        record, context = self.packet("02-block-and-pending")
        record["routing"] = []
        self.assertTrue(CHECK.validate(record, context))

    def test_a_declined_request_is_a_disposition_without_activating_the_proposal(self):
        record, context = self.packet("02-block-and-pending")
        request = context["norm_requests"][0]
        decision = {"outcome": "DECLINED", "principal_id": context["human_masters"][0],
                    "decision_ref": "example:decline-shelf", "norm_revision": request["norm_revision"],
                    "base_sha": context["inputs"]["base_sha"], "corpus_hash": context["inputs"]["corpus_hash"]}
        request["decision"] = decision
        record["routing"] = []
        record["norm_decisions"] = [{**decision, "request_id": request["request_id"]}]
        # Review the library under an existing rule after the decline. A separate opening violation survives.
        context["expected_scope"][1]["clauses"] = ["R-03"]
        record["clauses"].append({"clause": "R-03", "scope": "library", "required": True,
                                  "status": "PRESERVED", "evidence_ref": "reader/library"})
        self.assertEqual(self.rebind(record, context), [])
        self.assertEqual(record["canon_gate"], "NO-GO")

    def test_pending_question_can_precede_draft_text_and_acceptance_cannot(self):
        record, context = self.packet("01-pending")
        context["norm_requests"][0]["norm_revision"] = None
        self.assertEqual(self.rebind(record, context), [])
        record, context = self.packet()
        context["norm_requests"][0]["norm_revision"] = None
        self.assertTrue(self.rebind(record, context))

    def test_decision_must_be_present_independently_and_match_the_event(self):
        record, context = self.packet()
        for field, forged in (("principal_id", "Lead"), ("norm_revision", "f" * 64),
                              ("decision_ref", "another-event"), ("request_id", "another-request")):
            with self.subTest(field=field):
                changed = copy.deepcopy(record)
                changed["norm_decisions"][0][field] = forged
                self.assertTrue(CHECK.validate(changed, context))
        context["norm_requests"][0]["decision"] = None
        self.assertTrue(self.rebind(record, context))

    def test_even_matching_copies_require_a_trusted_human_revision_and_current_applicability(self):
        for field, bad in (("principal_id", "Lead"), ("norm_revision", "f" * 64),
                           ("base_sha", "0" * 40), ("corpus_hash", "1" * 64), ("outcome", "PENDING")):
            with self.subTest(field=field):
                record, context = self.packet()
                context["norm_requests"][0]["decision"][field] = bad
                record["norm_decisions"][0][field] = bad
                self.assertTrue(self.rebind(record, context))

    def test_context_binds_all_five_inputs_as_well_as_its_contents(self):
        for field in CHECK.INPUT_KEYS:
            with self.subTest(field=field):
                record, context = self.packet()
                record["inputs"][field] += "-replaced"
                self.assertTrue(CHECK.validate(record, context))
        record, context = self.packet()
        context["evidence"][0]["observation"] += " edited"
        self.assertTrue(CHECK.validate(record, context))
        self.assertTrue(CHECK.validate(record))
        self.assertTrue(CHECK.validate(record, []))

    def test_ambiguous_and_instability_routes_keep_their_own_authority(self):
        for kind, authority in (("NEEDS-RULING", "Council"), ("INSTABILITY", "Master"), ("CONTEXT", None)):
            with self.subTest(kind=kind):
                record, context = self.packet()
                route = {"kind": kind, "decision_authority": authority, "scope": "library",
                         "follow_up_owner": "Lead", "reason": "Unresolved question"}
                if kind == "NEEDS-RULING":
                    route["cite"] = "R-06"
                record["routing"] = [route]
                record["canon_gate"] = record["dialogue"]["final_gate"] = "HOLD"
                self.assertEqual(CHECK.validate(record, context), [])
                route["decision_authority"] = "Lead"
                self.assertTrue(CHECK.validate(record, context))

    def test_guarded_cli_rejects_legacy_template_and_examples(self):
        record, context = self.packet()
        self.assertTrue(CHECK.validate(record, context, require_review=True))
        # Simulate a real-kind integration in the isolated test only.
        record["record_kind"] = "review"
        self.assertTrue(CHECK.validate(record, context, require_review=True))
        context["context_kind"] = "review"
        self.rebind(record, context)
        self.assertEqual(CHECK.validate(record, context, require_review=True), [])
        for p in (ROOT / "examples/coordination/verdicts/block.json",
                  ROOT / "skills/cdd-guardian/references/verdict-template.json",
                  self.packets / "03-reassessed/verdict.json"):
            args = [sys.executable, str(self.cli), str(p), "--require-review"]
            self.assertNotEqual(subprocess.run(args, capture_output=True).returncode, 0)
        legacy = json.loads((ROOT / "examples/coordination/verdicts/block.json").read_text())
        self.assertEqual(CHECK.validate(legacy), [])
        self.assertTrue(CHECK.validate(legacy, context))

    def test_broken_field_types_are_errors_not_exceptions(self):
        for key, bad in (("norm_requests", [None]), ("evidence", [{"ref": []}]),
                         ("expected_scope", [{"scope": 3, "clauses": []}]), ("human_masters", [{}])):
            with self.subTest(key=key):
                record, context = self.packet()
                context[key] = bad
                self.assertTrue(self.rebind(record, context))


if __name__ == "__main__":
    unittest.main()
