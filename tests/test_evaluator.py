import unittest
import json
from pathlib import Path
from pydantic import ValidationError

from src.proofsec.schemas import CustomEvaluationRequest, CustomEvaluationResult
from src.proofsec.evaluator import CustomEvaluator
from src.proofsec.providers import MockProvider, ProviderStatus

class TestCustomEvaluator(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.success_mock = MockProvider(
            mock_response=CustomEvaluationResult(
                classification="Insufficient Evidence",
                evidence_state="PARTIAL",
                supporting_evidence=["Found X"],
                missing_evidence=["Need Y"],
                safe_verification=["Test Z"],
                impact="Low",
                reasoning="Because of X"
            )
        )
        self.fail_mock = MockProvider(
            mock_status=ProviderStatus.AUTHENTICATION_ERROR
        )
        
    def test_input_validation(self):
        # Missing scenario
        with self.assertRaises(ValidationError):
            CustomEvaluationRequest(evidence=["test"])
            
        # Valid input
        req = CustomEvaluationRequest(scenario="Test API", evidence=["ID is sequential"])
        self.assertEqual(req.scenario, "Test API")
        self.assertEqual(len(req.evidence), 1)

    def test_provider_failure_handling(self):
        evaluator = CustomEvaluator(provider=self.fail_mock)
        req = CustomEvaluationRequest(scenario="Test API")
        
        with self.assertRaises(RuntimeError) as context:
            evaluator.evaluate(req)
            
        self.assertIn("AUTHENTICATION_ERROR", str(context.exception))
        
    def test_provider_success(self):
        evaluator = CustomEvaluator(provider=self.success_mock)
        req = CustomEvaluationRequest(scenario="Test API")
        result = evaluator.evaluate(req)
        
        self.assertEqual(result.classification, "Insufficient Evidence")
        self.assertEqual(result.evidence_state, "PARTIAL")
        
    def test_research_isolation(self):
        # Verify custom evaluation does not touch research tasks
        tasks_dir = self.root / "tasks"
        raw_dir = self.root / "results" / "raw"
        
        # Count tasks before
        task_files = list(tasks_dir.glob("**/*.json"))
        raw_files = list(raw_dir.glob("**/*.json"))
        
        evaluator = CustomEvaluator(provider=self.success_mock)
        req = CustomEvaluationRequest(scenario="Test API")
        res = evaluator.evaluate(req)
        evaluator.save_evaluation(req, res)
        
        # Count tasks after
        task_files_after = list(tasks_dir.glob("**/*.json"))
        raw_files_after = list(raw_dir.glob("**/*.json"))
        
        self.assertEqual(len(task_files), len(task_files_after))
        self.assertEqual(len(raw_files), len(raw_files_after))
        
        # Verify it went to custom_evaluations
        custom_dir = self.root / "custom_evaluations"
        self.assertTrue(custom_dir.exists())
        self.assertGreater(len(list(custom_dir.glob("*.json"))), 0)

if __name__ == '__main__':
    unittest.main()

