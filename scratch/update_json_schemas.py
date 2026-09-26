import json
import glob
from pathlib import Path

def update_tasks():
    task_files = glob.glob("tasks/**/*.json", recursive=True)
    for f in task_files:
        with open(f, 'r', encoding='utf-8') as file:
            data = json.load(file)
            
        # Migrate metadata
        meta = data.get('metadata', {})
        
        # Determine evidence state from expected classification
        expected = data.get('ground_truth', {}).get('classification', '')
        if expected == 'Insufficient Evidence':
            evidence_state = 'WEAK'
        elif 'contradict' in data.get('id', ''):
            evidence_state = 'CONTRADICTORY'
        else:
            evidence_state = 'DECISIVE'
            
        data['evidence_state'] = evidence_state
        data['task_family'] = meta.get('perturbation_group', 'v1_baseline')
        data['paired_task_id'] = None
        data['decisive_fact'] = None
        data['research_tags'] = [meta.get('security_domain', data.get('category'))]
        
        # Remove old meta if not needed, or keep it.
        # Ensure new schema fields are at the top level
        with open(f, 'w', encoding='utf-8') as file:
            json.dump(data, file, indent=4)
            
if __name__ == '__main__':
    update_tasks()
    print("Updated JSON files")
