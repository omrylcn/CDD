import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


INIT = load('cdd_init', ROOT/'skills/cdd-init/scripts/init_cdd.py')
CHECK = load('cdd_check', ROOT/'skills/cdd-guardian/scripts/check_verdict.py')


class InitTests(unittest.TestCase):
    def test_dry_run_creates_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'product'
            planned, unchanged = INIT.initialize(target, dry_run=True)
            self.assertIn('CANON.md', planned)
            self.assertFalse(target.exists())

    def test_drafts_and_repeat_are_safe(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)/'product'
            planned, _ = INIT.initialize(target)
            self.assertEqual(len(planned), 5)
            before = {p.name:p.read_bytes() for p in target.iterdir()}
            self.assertIn('DRAFT', (target/'CANON.md').read_text())
            created, same = INIT.initialize(target)
            self.assertEqual(created, [])
            self.assertEqual(len(same), 5)
            self.assertEqual(before, {p.name:p.read_bytes() for p in target.iterdir()})

    def test_conflicting_agents_prevents_all_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target/'AGENTS.md').write_text('existing rules')
            with self.assertRaises(ValueError):
                INIT.initialize(target)
            self.assertEqual([p.name for p in target.iterdir()], ['AGENTS.md'])
            self.assertEqual((target/'AGENTS.md').read_text(), 'existing rules')

    def test_skip_agents_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp)
            (target/'AGENTS.md').write_text('existing rules')
            created, _ = INIT.initialize(target, skip_agents=True)
            self.assertEqual(len(created), 4)
            self.assertEqual((target/'AGENTS.md').read_text(), 'existing rules')

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp)/'product'; target.mkdir()
            other=Path(tmp)/'outside.md'; other.write_text('keep')
            (target/'CANON.md').symlink_to(other)
            with self.assertRaises(ValueError):
                INIT.initialize(target)
            self.assertEqual(other.read_text(), 'keep')
            self.assertFalse((target/'AGENTS.md').exists())


class VerdictTests(unittest.TestCase):
    def fixture(self, name):
        return json.loads((ROOT/f'examples/coordination/verdicts/{name}.json').read_text())

    def test_synthetic_examples_and_template(self):
        paths=list((ROOT/'examples/coordination/verdicts').glob('*.json'))
        paths += [ROOT/'skills/cdd-guardian/references/verdict-template.json']
        for path in paths:
            with self.subTest(path=path.name):
                self.assertEqual(CHECK.validate(json.loads(path.read_text())), [])

    def test_block_cannot_be_marked_go(self):
        r=self.fixture('block'); r['canon_gate']='GO'
        self.assertTrue(CHECK.validate(r))

    def test_open_work_survives_block(self):
        r=self.fixture('block')
        r['routing']=self.fixture('context')['routing']
        self.assertEqual(CHECK.validate(r), [])

    def test_advisory_count_does_not_hold_gate(self):
        r=self.fixture('advisory'); r['findings'] *= 10
        self.assertEqual(CHECK.validate(r), [])

    def test_not_assessed_and_context_cannot_silently_pass(self):
        r=self.fixture('context'); r['routing']=[]; r['scope']['unresolved']=[]; r['canon_gate']='GO'
        self.assertTrue(CHECK.validate(r))

    def test_duplicate_clause_scope_is_invalid(self):
        r=self.fixture('block'); c=copy.deepcopy(r['clauses'][0]); c['status']='PRESERVED'; r['clauses'].append(c)
        self.assertTrue(CHECK.validate(r))

    def test_block_without_counterexample_is_invalid(self):
        r=self.fixture('block'); del r['findings'][0]['counterexample']
        self.assertTrue(CHECK.validate(r))

    def test_real_review_requires_real_revision_fields(self):
        r=self.fixture('block'); r['record_kind']='review'
        self.assertTrue(CHECK.validate(r))

    def test_invalid_field_types_are_rejected(self):
        r=self.fixture('block')
        r['record_kind']=[]; r['canon_gate']=[]
        r['clauses'][0]['status']=[]; r['findings'][0]['severity']=[]
        r['routing']=[{'kind':[], 'reason':'x', 'owner':'x'}]
        self.assertTrue(CHECK.validate(r))

    def test_empty_resolved_scope_is_invalid(self):
        r=self.fixture('advisory'); r['scope']['selection']=[]
        self.assertTrue(CHECK.validate(r))


if __name__=='__main__':
    unittest.main()
