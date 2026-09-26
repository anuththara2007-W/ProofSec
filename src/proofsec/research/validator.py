import json
from typing import Dict, Any, Tuple
import difflib

class OneFactFlipValidator:
    """
    Validates that a pair of tasks differ ONLY by the intended fact.
    """
    
    @staticmethod
    def validate_pair(task_a: Dict[str, Any], task_b: Dict[str, Any]) -> Tuple[bool, str]:
        # Both must have metadata
        meta_a = task_a.get("metadata", {}).get("one_fact_flip")
        if not meta_a:
            return False, "Task A missing one_fact_flip metadata"
            
        if meta_a["paired_task_id"] != task_b["id"]:
            return False, f"Task A paired_task_id ({meta_a['paired_task_id']}) does not match Task B id ({task_b['id']})"
            
        # Check that unchanged facts are present in both
        scenario_a = task_a.get("scenario", "")
        scenario_b = task_b.get("scenario", "")
        evidence_a = " ".join(task_a.get("evidence", []))
        evidence_b = " ".join(task_b.get("evidence", []))
        
        text_a = f"{scenario_a} {evidence_a}"
        text_b = f"{scenario_b} {evidence_b}"
        
        for fact in meta_a.get("unchanged_facts", []):
            if fact not in text_a:
                return False, f"Unchanged fact '{fact}' missing from Task A"
            if fact not in text_b:
                return False, f"Unchanged fact '{fact}' missing from Task B"
                
        # Compare texts for unintended changes (simplified diff check)
        seq = difflib.SequenceMatcher(None, text_a, text_b)
        ratio = seq.ratio()
        
        # We expect a high degree of similarity for a ONE-fact flip.
        if ratio < 0.7:
            return False, f"Tasks are too dissimilar (similarity {ratio:.2f}). Too many facts changed."
            
        return True, "Valid"
