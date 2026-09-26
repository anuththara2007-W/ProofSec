import argparse
import sys
import os
import json
from pathlib import Path

# Setup paths
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from src.proofsec.schemas import CustomEvaluationRequest
from src.proofsec.evaluator import CustomEvaluator

def main():
    parser = argparse.ArgumentParser(description="ProofSec Custom Evaluation CLI")
    parser.add_argument('--file', type=str, help="Path to a JSON file containing the evaluation request")
    parser.add_argument('--provider', type=str, help="Provider to use (e.g., kaggle, openai_compatible)", default="kaggle")
    
    args = parser.parse_args()
    
    if args.provider:
        os.environ['PROOFSEC_PROVIDER'] = args.provider
    
    if args.file:
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            request = CustomEvaluationRequest(**data)
        except Exception as e:
            print(f"Error loading file: {e}")
            sys.exit(1)
    else:
        print("ProofSec Custom Evaluation\n")
        scenario = input("Scenario:\n> ")
        evidence_input = input("\nEvidence (comma separated, or leave blank):\n> ")
        evidence = [e.strip() for e in evidence_input.split(",")] if evidence_input else []
        context = input("\nAdditional context (optional):\n> ")
        
        confirm = input("\nEvaluate? [Y/n] ")
        if confirm.lower() not in ['', 'y', 'yes']:
            print("Aborted.")
            sys.exit(0)
            
        request = CustomEvaluationRequest(
            scenario=scenario,
            evidence=evidence,
            context=context if context else None
        )
        
    evaluator = CustomEvaluator()
    print("\nEvaluating...\n")
    
    try:
        result = evaluator.evaluate(request)
    except Exception as e:
        print(f"EVALUATION FAILURE: {e}")
        sys.exit(1)
        
    evaluator.save_evaluation(request, result)
    
    print("────────────────────────────────")
    print("PROOFSEC RESULT")
    print("────────────────────────────────\n")
    print(f"Classification:\n{result.classification}\n")
    print(f"Evidence State:\n{result.evidence_state}\n")
    
    print("Supporting Evidence:")
    for ev in result.supporting_evidence:
        print(f"- {ev}")
    print()
    
    print("Missing Evidence:")
    for ev in result.missing_evidence:
        print(f"- {ev}")
    print()
        
    print("Safe Verification:")
    for sv in result.safe_verification:
        print(f"- {sv}")
    print()
        
    print(f"Potential Impact:\n{result.impact}\n")
    print(f"Reasoning:\n{result.reasoning}\n")

if __name__ == "__main__":
    main()
