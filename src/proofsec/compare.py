from typing import Dict, Any, Optional
from proofsec.schemas import EvaluationResponse, CustomEvaluationRequest

class CompareEngine:
    @staticmethod
    def compare_evaluations(eval_a: EvaluationResponse, eval_b: EvaluationResponse) -> Dict[str, Any]:
        """
        Compare two evaluations (usually revisions of the same scenario).
        """
        classification_changed = eval_a.classification != eval_b.classification
        evidence_state_changed = eval_a.evidence_state != eval_b.evidence_state
        impact_changed = eval_a.impact != eval_b.impact

        set_a_supp = set(eval_a.supporting_evidence)
        set_b_supp = set(eval_b.supporting_evidence)
        supp_added = list(set_b_supp - set_a_supp)
        supp_removed = list(set_a_supp - set_b_supp)

        set_a_miss = set(eval_a.missing_evidence)
        set_b_miss = set(eval_b.missing_evidence)
        miss_added = list(set_b_miss - set_a_miss)
        miss_removed = list(set_a_miss - set_b_miss)

        return {
            "classification_changed": classification_changed,
            "classification_transition": f"{eval_a.classification} -> {eval_b.classification}" if classification_changed else None,
            "evidence_state_changed": evidence_state_changed,
            "evidence_state_transition": f"{eval_a.evidence_state} -> {eval_b.evidence_state}" if evidence_state_changed else None,
            "impact_changed": impact_changed,
            "supporting_evidence_added": supp_added,
            "supporting_evidence_removed": supp_removed,
            "missing_evidence_added": miss_added,
            "missing_evidence_removed": miss_removed
        }

    @staticmethod
    def calculate_metrics(request: CustomEvaluationRequest, response: EvaluationResponse) -> Dict[str, Any]:
        """
        Calculate metrics based on user-provided ground truth.
        """
        if not request.expected_classification and not request.expected_evidence_state and not request.expected_decisive_fact:
            return {"status": "Ground truth not provided"}

        metrics = {}
        
        if request.expected_classification:
            correct = (request.expected_classification.lower() == response.classification.lower())
            metrics["classification_correct"] = correct

        if request.expected_evidence_state:
            correct = (request.expected_evidence_state.lower() == response.evidence_state.lower())
            metrics["evidence_state_correct"] = correct

        # If both are provided, accuracy can be strict (both correct) or just classification correct
        if "classification_correct" in metrics:
            metrics["accuracy"] = 1.0 if metrics["classification_correct"] else 0.0

        return metrics
