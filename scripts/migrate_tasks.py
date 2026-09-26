import ast
import json
import os
import re

def slugify(value):
    value = str(value).lower()
    value = re.sub(r'[^a-z0-9\s-]', '', value)
    value = re.sub(r'[-\s]+', '-', value).strip('-_')
    return value

def extract_tasks_from_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    tree = ast.parse(content)
    tasks = []

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            is_task = False
            task_name = ""
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and getattr(decorator.func, 'attr', '') == 'task':
                    is_task = True
                    for kwd in decorator.keywords:
                        if kwd.arg == 'name':
                            task_name = kwd.value.value
            
            if not is_task:
                continue

            scenario = ""
            expected = ""
            expectation = ""
            
            for stmt in node.body:
                if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1 and getattr(stmt.targets[0], 'id', '') == 'scenario':
                    scenario = stmt.value.value
                elif isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
                    if getattr(getattr(stmt.value.func, 'value', None), 'id', '') == 'assertions' and getattr(stmt.value.func, 'attr', '') == 'assert_equal':
                        for kwd in stmt.value.keywords:
                            if kwd.arg == 'expected':
                                expected = kwd.value.value
                            elif kwd.arg == 'expectation':
                                expectation = kwd.value.value

            tasks.append({
                "title": task_name,
                "scenario": scenario,
                "expected": expected,
                "expectation": expectation
            })
            
    return tasks

def categorize_task(title):
    t = title.lower()
    if 'idor' in t or 'bola' in t: return 'idor'
    if 'sqli' in t: return 'sqli'
    if 'ssrf' in t: return 'ssrf'
    if 'auth' in t or 'bypass' in t or 'jwt' in t or 'session' in t or 'httponly' in t: return 'authentication'
    if 'rate limit' in t: return 'rate_limiting'
    if 'business logic' in t: return 'business_logic'
    if 'claim' in t or 'trap' in t or 'contradiction' in t: return 'terminology_traps'
    if 'info' in t or 'disclosure' in t: return 'information_disclosure'
    if 'headers' in t: return 'security_headers'
    return 'terminology_traps'

def main():
    tasks = extract_tasks_from_file('legacy/proofsec.py')
    
    for i, t in enumerate(tasks):
        title = t['title']
        cat = categorize_task(title)
        task_id = f"task-{i+1:03d}-{slugify(title)}"
        
        task_obj = {
            "id": task_id,
            "title": title,
            "category": cat,
            "experiment": "migrated_baseline",
            "scenario": t['scenario'],
            "evidence": {
                "available": [],
                "missing": [],
                "decisive": [],
                "irrelevant": []
            },
            "ground_truth": {
                "classification": t['expected'],
                "rationale": t['expectation']
            },
            "metadata": {
                "difficulty": "medium",
                "security_domain": cat,
                "version": "1.0"
            }
        }
        
        filepath = f"tasks/{cat}/{task_id}.json"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(task_obj, f, indent=4)
        print(f"Migrated {task_id}")

if __name__ == '__main__':
    main()
