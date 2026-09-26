import unittest
import os
import json
from pathlib import Path

from proofsec.client import ProofSec
from proofsec.schemas import EvaluationResponse

class TestProofSecSDK(unittest.TestCase):
    def setUp(self):
        os.environ['PROOFSEC_PROVIDER'] = 'mock'
        self.client = ProofSec()

    def tearDown(self):
        if 'PROOFSEC_PROVIDER' in os.environ:
            del os.environ['PROOFSEC_PROVIDER']

    def test_evaluate(self):
        result = self.client.evaluate(
            scenario="Test Scenario",
            evidence=["Test Evidence"],
            save=True
        )
        self.assertIsInstance(result, EvaluationResponse)
        self.assertEqual(result.classification, "Insufficient Evidence")
        self.assertTrue(result.evaluation_id.startswith("eval-"))

    def test_health(self):
        health = self.client.health()
        self.assertEqual(health.provider, "mock")
        
    def test_revise_evaluation(self):
        res1 = self.client.evaluate(scenario="Test Revision", save=True)
        res2 = self.client.revise(res1.evaluation_id, evidence=["New Evidence"])
        self.assertEqual(res2.previous_evaluation_id, res1.evaluation_id)
        self.assertNotEqual(res1.evaluation_id, res2.evaluation_id)
