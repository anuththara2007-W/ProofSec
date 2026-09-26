import unittest
from evaluation.recompute_metrics import compute_metrics_from_data

class TestMetricsEngine(unittest.TestCase):
    def setUp(self):
        self.mock_tasks = {
            'task-1': {
                'id': 'task-1',
                'ground_truth': {'classification': 'Vulnerable'}
            },
            'task-2': {
                'id': 'task-2',
                'ground_truth': {'classification': 'Not Vulnerable'}
            },
            'task-3': {
                'id': 'task-3',
                'ground_truth': {'classification': 'Not Vulnerable'}
            }
        }
        
    def test_partial_denominators(self):
        # Only 2 out of 3 tasks completed
        mock_responses = {
            'task-1': {'classification': 'Vulnerable'},
            'task-2': {'classification': 'Vulnerable'}
        }
        
        metrics = compute_metrics_from_data(self.mock_tasks, mock_responses)
        
        # Accuracy: task-1 is correct, task-2 is incorrect (Vulnerable instead of Not Vulnerable)
        # Denominator should be 2, not 3
        self.assertEqual(metrics['acc'], 0.5)
        
        # PVR: Eligible is task-2 and task-3 (Not Vulnerable). But only task-2 is in responses.
        # So eligible is 1, and it failed (returned Vulnerable). So PVR = 1.0
        self.assertEqual(metrics['pvr'], 1.0)
        
    def test_missing_tasks_do_not_enter_pvr_denominator(self):
        mock_responses = {
            'task-1': {'classification': 'Vulnerable'} # Not eligible for PVR
        }
        metrics = compute_metrics_from_data(self.mock_tasks, mock_responses)
        
        self.assertEqual(metrics['acc'], 1.0)
        self.assertEqual(metrics['pvr'], 0.0) # Denominator 0 -> PVR 0
        
if __name__ == '__main__':
    unittest.main()
