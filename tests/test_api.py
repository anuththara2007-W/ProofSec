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
from src.proofsec.providers import MockProvider

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Force mock provider globally
        os.environ['PROOFSEC_PROVIDER'] = 'mock'
        
        cls.port = 8081
        cls.server = HTTPServer(('127.0.0.1', cls.port), ProofSecAPIHandler)
        cls.thread = Thread(target=cls.server.serve_forever)
        cls.thread.daemon = True
        cls.thread.start()
        time.sleep(0.1) # Wait for server to start
        
    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()
        
    def setUp(self):
        self.root = Path(__file__).parent.parent
        self.url = f"http://127.0.0.1:{self.port}/api/v1/evaluate"
        
    def test_valid_request(self):
        req = urllib.request.Request(self.url, method='POST')
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"scenario": "Test", "evidence": ["None"]}).encode('utf-8')
        
        try:
            with urllib.request.urlopen(req, data=data) as response:
                self.assertEqual(response.status, 200)
                body = json.loads(response.read().decode('utf-8'))
                self.assertIn('classification', body)
        except urllib.error.HTTPError as e:
            self.fail(f"Request failed with {e.code}")

    def test_invalid_schema(self):
        req = urllib.request.Request(self.url, method='POST')
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"wrong": "payload"}).encode('utf-8')
        
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            urllib.request.urlopen(req, data=data)
            
        self.assertEqual(ctx.exception.code, 422)

    def test_research_isolation(self):
        tasks_dir = self.root / "tasks"
        raw_dir = self.root / "results" / "raw"
        
        task_files = list(tasks_dir.glob("**/*.json"))
        raw_files = list(raw_dir.glob("**/*.json"))
        
        req = urllib.request.Request(self.url, method='POST')
        req.add_header('Content-Type', 'application/json')
        data = json.dumps({"scenario": "Isolation Test", "evidence": []}).encode('utf-8')
        urllib.request.urlopen(req, data=data)
        
        task_files_after = list(tasks_dir.glob("**/*.json"))
        raw_files_after = list(raw_dir.glob("**/*.json"))
        
        self.assertEqual(len(task_files), len(task_files_after))
        self.assertEqual(len(raw_files), len(raw_files_after))

if __name__ == '__main__':
    unittest.main()
