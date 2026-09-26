import unittest
import json
from pathlib import Path
from http.server import HTTPServer
from threading import Thread
import urllib.request
import urllib.error
import time
import os

from scripts.api import ProofSecAPIHandler

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
        from evaluation.verify_frozen_benchmark import calculate_dataset_hash
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


if __name__ == '__main__':
    unittest.main()
