import unittest
import unittest.mock
import json
from pathlib import Path
from http.server import HTTPServer
from threading import Thread
import urllib.request
import urllib.error
import time
import os

from proofsec.api import ProofSecAPIHandler

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        os.environ['PROOFSEC_PROVIDER'] = 'mock'
        cls.port = 8082
        cls.server = HTTPServer(('127.0.0.1', cls.port), ProofSecAPIHandler)
        cls.thread = Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(0.2)

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        if 'PROOFSEC_PROVIDER' in os.environ:
            del os.environ['PROOFSEC_PROVIDER']

    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.url = f"http://127.0.0.1:{self.port}/api/v1/evaluate"

    def _post(self, data_dict):
        req = urllib.request.Request(self.url, method='POST')
        req.add_header('Content-Type', 'application/json')
        return urllib.request.urlopen(req, json.dumps(data_dict).encode('utf-8'))

    def test_valid_request_returns_200(self):
        with self._post({"scenario": "Test", "evidence": ["obs"]}) as resp:
            self.assertEqual(resp.status, 200)
            body = json.loads(resp.read().decode('utf-8'))
            self.assertIn('classification', body)
            self.assertIn('evaluation_id', body)
            self.assertIn('evidence_state', body)

    def test_invalid_json_returns_400(self):
        req = urllib.request.Request(self.url, method='POST')
        req.add_header('Content-Type', 'application/json')
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, b"not-json{{{")
        self.assertEqual(ctx.exception.code, 400)

    def test_missing_scenario_returns_422(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self._post({"wrong": "payload"})
        self.assertEqual(ctx.exception.code, 422)

    def test_research_isolation(self):
        tasks_dir = self.root / "tasks"
        raw_dir = self.root / "results" / "raw"
        task_count = len(list(tasks_dir.glob("**/*.json")))
        raw_count = len(list(raw_dir.glob("**/*.json")))

        self._post({"scenario": "Isolation Test", "evidence": []})

        self.assertEqual(task_count, len(list(tasks_dir.glob("**/*.json"))))
        self.assertEqual(raw_count, len(list(raw_dir.glob("**/*.json"))))

    def test_benchmark_hash_unchanged(self):
        from proofsec.research import calculate_dataset_hash
        tasks_dir = self.root / "tasks"
        h = calculate_dataset_hash(str(tasks_dir))
        self.assertEqual(h, "422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80")

    def test_404_on_wrong_path(self):
        req = urllib.request.Request(f"http://127.0.0.1:{self.port}/api/v1/wrong", method='POST')
        req.add_header('Content-Type', 'application/json')
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, b'{}')
        self.assertEqual(ctx.exception.code, 404)

    def test_no_secrets_in_response(self):
        """API response must not leak credentials."""
        with self._post({"scenario": "Secret test"}) as resp:
            body = resp.read().decode('utf-8')
            self.assertNotIn("api_key", body.lower())
            self.assertNotIn("authorization", body.lower())

    def test_kaggle_auth_failure_returns_502(self):
        """Test the regression case for Kaggle 502 structured error."""
        # Force provider to kaggle
        os.environ['PROOFSEC_PROVIDER'] = 'kaggle'
        # Since we likely don't have valid kaggle credentials in the test env, it should fail
        # Or even if it's not configured, it returns 503 or 502
        try:
            req = urllib.request.Request(self.url, method='POST')
            req.add_header('Content-Type', 'application/json')
            urllib.request.urlopen(req, b'{"scenario": "Test"}')
            self.fail("Expected HTTPError")
        except urllib.error.HTTPError as e:
            self.assertIn(e.code, [502, 503])
            body = json.loads(e.read().decode('utf-8'))
            self.assertIn("error", body)
            self.assertIn(body["error"]["code"], ["AUTHENTICATION_ERROR", "CONFIGURATION_ERROR"])
            self.assertEqual(body["error"]["provider"], "kaggle")
        finally:
            os.environ['PROOFSEC_PROVIDER'] = 'mock'


if __name__ == '__main__':
    unittest.main()

    def test_research_api_returns_200(self):
        req = urllib.request.Request(f'http://127.0.0.1:{self.port}/api/v1/research/metrics', method='GET')
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            body = json.loads(resp.read().decode('utf-8'))
            self.assertIn('benchmark', body)


    def test_mock_evaluate_returns_200(self):
        with self._post({'scenario': 'Test', 'provider': 'mock'}) as resp:
            self.assertEqual(resp.status, 200)
            body = json.loads(resp.read().decode('utf-8'))
            self.assertEqual(body['status'], 'completed')
            self.assertIn('classification', body['result'])

    @unittest.mock.patch('proofsec.api.CustomEvaluator.evaluate', side_effect=RuntimeError('simulated error'))
    def test_unexpected_exception_returns_500(self, mock_eval):
        try:
            req = urllib.request.Request(self.url, method='POST')
            req.add_header('Content-Type', 'application/json')
            urllib.request.urlopen(req, b'{"scenario": "Test"}')
            self.fail('Expected HTTPError')
        except urllib.error.HTTPError as e:
            self.assertEqual(e.code, 500)
            body = json.loads(e.read().decode('utf-8'))
            self.assertEqual(body['status'], 'failed')
            self.assertEqual(body['error']['code'], 'INTERNAL_ERROR')


