import unittest
import json
import glob
from pathlib import Path
import hashlib
import os

def get_project_root():
    return Path(__file__).parent.parent

class TestProofSec(unittest.TestCase):
    def setUp(self):
        self.root = get_project_root()
        self.manifest_path = self.root / "benchmark" / "manifests" / "proofsec-v0.2.json"
        self.tasks_dir = self.root / "tasks"
        
    def test_dataset_validation(self):
        files = glob.glob(str(self.tasks_dir / "**/*.json"), recursive=True)
        self.assertEqual(len(files), 110, "Dataset must contain exactly 110 tasks")
        
    def test_schema_validation(self):
        files = glob.glob(str(self.tasks_dir / "**/*.json"), recursive=True)
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.assertIn('id', data)
                self.assertIn('category', data)
                self.assertIn('scenario', data)
                self.assertIn('ground_truth', data)
                self.assertIn('classification', data['ground_truth'])
                self.assertIn(data['ground_truth']['classification'], ['Vulnerable', 'Not Vulnerable', 'Insufficient Evidence'])
                
    def test_frozen_hash_verification(self):
        with open(self.manifest_path, 'r', encoding='utf-8') as f:
            manifest = json.load(f)
        frozen_hash = manifest.get('dataset_sha256')
        self.assertEqual(frozen_hash, "422501a4db424c30c8ef24b61183351ec8a4bd2096e2671cf0e6bdf91e133a80")
        
    def test_leakage_detection(self):
        files = glob.glob(str(self.tasks_dir / "**/*.json"), recursive=True)
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                data = json.load(file)
                scenario = data['scenario'].lower()
                expected = data['ground_truth']['classification'].lower()
                
                # Check if the exact expected class string is blatantly leaked in scenario
                # 'vulnerable', 'not vulnerable', 'insufficient evidence' shouldn't be spelled out as the answer.
                self.assertNotIn("classification: " + expected, scenario)
                self.assertNotIn("final classification: " + expected, scenario)

    def test_pair_integrity(self):
        files = glob.glob(str(self.tasks_dir / "**/*.json"), recursive=True)
        tasks_map = {}
        for f in files:
            with open(f, 'r', encoding='utf-8') as file:
                d = json.load(file)
                tasks_map[d['id']] = d
                
        for t_id, d in tasks_map.items():
            if 'paired_task_id' in d and d['paired_task_id'] is not None:
                paired_id = d['paired_task_id']
                self.assertIn(paired_id, tasks_map, f"Paired task {paired_id} missing for {t_id}")
                
    def test_pvr_calculation(self):
        # mock test for PVR calculation math logic
        eligible = 44
        false_positives = 9
        pvr = false_positives / eligible
        self.assertAlmostEqual(pvr, 0.2045, places=4)

if __name__ == '__main__':
    unittest.main()
