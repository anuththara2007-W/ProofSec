import unittest
import sys
from unittest.mock import patch
from io import StringIO

from proofsec.cli import main

class TestCLI(unittest.TestCase):
    @patch('sys.stdout', new_callable=StringIO)
    def test_version_command(self, mock_stdout):
        test_args = ["proofsec", "version"]
        with patch.object(sys, 'argv', test_args):
            main()
        self.assertIn("ProofSec Custom Evaluation Version", mock_stdout.getvalue())

    @patch('sys.stdout', new_callable=StringIO)
    def test_health_command(self, mock_stdout):
        test_args = ["proofsec", "health", "--provider", "mock"]
        with patch.object(sys, 'argv', test_args):
            main()
        self.assertIn("Provider", mock_stdout.getvalue())
        self.assertIn("mock", mock_stdout.getvalue())
        self.assertIn("AVAILABLE", mock_stdout.getvalue())
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_benchmark_hash(self, mock_stdout):
        test_args = ["proofsec", "benchmark", "hash"]
        with patch.object(sys, 'argv', test_args):
            main()
        self.assertIn("Benchmark SHA256", mock_stdout.getvalue())
        
    @patch('sys.stdout', new_callable=StringIO)
    def test_research_metrics(self, mock_stdout):
        test_args = ["proofsec", "research", "metrics"]
        with patch.object(sys, 'argv', test_args):
            main()
        self.assertIn("Historical Gemini 3.5 Flash Results", mock_stdout.getvalue())
