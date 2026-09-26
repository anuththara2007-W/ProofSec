import unittest
from proofsec.research.validator import OneFactFlipValidator
from proofsec.schemas import CustomEvaluationRequest, EvaluationResponse
from proofsec.compare import CompareEngine

class TestResearchFeatures(unittest.TestCase):
    def test_one_fact_flip_validator(self):
        task_a = {
            "id": "t1",
            "scenario": "A user logs in.",
            "evidence": ["Session established."],
            "metadata": {
                "one_fact_flip": {
                    "paired_task_id": "t2",
                    "changed_fact": "No MFA used",
                    "unchanged_facts": ["user logs in", "Session established"],
                    "expected_transition": "Not Vulnerable -> Vulnerable",
                    "evidence_state_before": "WEAK",
                    "evidence_state_after": "DECISIVE"
                }
            }
        }
        
        task_b = {
            "id": "t2",
            "scenario": "A user logs in.",
            "evidence": ["Session established.", "No MFA used."]
        }
        
        # Valid pair
        valid, msg = OneFactFlipValidator.validate_pair(task_a, task_b)
        self.assertTrue(valid, msg)
        
        # Invalid pair: missing unchanged fact
        task_b_bad = {
            "id": "t2",
            "scenario": "An admin logs out.",
            "evidence": ["Session established.", "No MFA used."]
        }
        valid, msg = OneFactFlipValidator.validate_pair(task_a, task_b_bad)
        self.assertFalse(valid)
        self.assertIn("missing from Task B", msg)

    def test_compare_engine(self):
        req = CustomEvaluationRequest(
            scenario="Test",
            expected_classification="Vulnerable",
            expected_evidence_state="DECISIVE"
        )
        
        res = EvaluationResponse(
            evaluation_id="e1",
            version="1.0",
            classification="Vulnerable",
            evidence_state="DECISIVE",
            confidence=90,
            confidence_status="AVAILABLE",
            summary="",
            supporting_evidence=[],
            missing_evidence=[],
            contradicting_evidence=[],
            safe_verification=[],
            impact="",
            reasoning="",
            provider="mock",
            model="mock-v1",
            created_at="2023-01-01T00:00:00Z",
            previous_evaluation_id=None
        )
        
        metrics = CompareEngine.calculate_metrics(req, res)
        self.assertTrue(metrics["classification_correct"])
        self.assertTrue(metrics["evidence_state_correct"])
        self.assertEqual(metrics["accuracy"], 1.0)
        
    def test_compare_engine_evaluations(self):
        res_a = EvaluationResponse(
            evaluation_id="e1",
            version="1.0",
            classification="Insufficient Evidence",
            evidence_state="WEAK",
            confidence=50,
            confidence_status="AVAILABLE",
            summary="",
            supporting_evidence=["Observed X"],
            missing_evidence=["Missing Y"],
            contradicting_evidence=[],
            safe_verification=[],
            impact="",
            reasoning="",
            provider="mock",
            model="mock",
            created_at="2023-01-01T00:00:00Z"
        )
        
        res_b = EvaluationResponse(
            evaluation_id="e2",
            version="1.0",
            classification="Vulnerable",
            evidence_state="DECISIVE",
            confidence=90,
            confidence_status="AVAILABLE",
            summary="",
            supporting_evidence=["Observed X", "Observed Y"],
            missing_evidence=[],
            contradicting_evidence=[],
            safe_verification=[],
            impact="High",
            reasoning="",
            provider="mock",
            model="mock",
            created_at="2023-01-01T01:00:00Z"
        )
        
        diff = CompareEngine.compare_evaluations(res_a, res_b)
        self.assertTrue(diff["classification_changed"])
        self.assertTrue(diff["evidence_state_changed"])
        self.assertTrue(diff["impact_changed"])
        self.assertIn("Observed Y", diff["supporting_evidence_added"])
        self.assertIn("Missing Y", diff["missing_evidence_removed"])

if __name__ == '__main__':
    unittest.main()
