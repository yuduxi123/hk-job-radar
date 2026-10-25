import importlib.util
from pathlib import Path
import unittest
spec = importlib.util.spec_from_file_location("match_evidence", Path(__file__).resolve().parents[1] / "scripts/match_evidence.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
class EvidenceTests(unittest.TestCase):
    def sample(self, state="met", status="open"):
        return dict(status=status, core_match=True, requirements=[dict(requirement="graduation window", hard=True, state=state, evidence="candidate record")])
    def test_unknown_does_not_pass_or_reject(self):
        self.assertEqual(m.evaluate(self.sample("unknown"))["grade"], "B")
    def test_hard_conflict_blocks_recommendation(self):
        self.assertFalse(m.evaluate(self.sample("not_met"))["recommendable"])
    def test_closed_even_if_skills_match(self):
        self.assertEqual(m.evaluate(self.sample(status="closed"))["grade"], "C")
    def test_qualifies(self):
        self.assertEqual(m.evaluate(self.sample())["grade"], "A")
    def test_missing_evidence_fails(self):
        d=self.sample();d["requirements"][0]["evidence"]=""
        with self.assertRaises(ValueError):m.evaluate(d)
    def test_unverified_cannot_be_a(self):
        self.assertEqual(m.evaluate(self.sample(status="unverified"))["grade"], "B")
