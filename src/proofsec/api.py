import json
import sys
import re
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from proofsec.schemas import CustomEvaluationRequest, CUSTOM_EVALUATION_VERSION
from proofsec.evaluator import CustomEvaluator
from proofsec.providers import get_provider
from pydantic import ValidationError

class ProofSecAPIHandler(BaseHTTPRequestHandler):
    
    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if path == '/api/v1/health':
            provider = get_provider()
            health = provider.health_check()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(health.model_dump_json().encode('utf-8'))
            return

        if path == '/api/v1/providers':
            providers = [
                {"id": "kaggle", "description": "Kaggle Models API"},
                {"id": "openai_compatible", "description": "OpenAI-compatible endpoint"},
                {"id": "mock", "description": "Test fixture"}
            ]
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"providers": providers}).encode('utf-8'))
            return

        if path == '/api/v1/version':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"version": CUSTOM_EVALUATION_VERSION}).encode('utf-8'))
            return

        if path == '/api/v1/schema':
            schema = CustomEvaluationRequest.model_json_schema()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(schema).encode('utf-8'))
            return

        match = re.match(r'^/api/v1/evaluations/([a-zA-Z0-9_\-]+)$', path)
        if match:
            eval_id = match.group(1)
            evaluator = CustomEvaluator()
            evaluation = evaluator.get_evaluation(eval_id)
            if not evaluation:
                self._send_error(404, "Evaluation not found")
                return
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(evaluation.model_dump_json().encode('utf-8'))
            return

        self._send_error(404, "Not Found")

    def do_POST(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON payload")
            return

        if path == '/api/v1/evaluate':
            self._handle_evaluate(payload)
            return

        match = re.match(r'^/api/v1/evaluations/([a-zA-Z0-9_\-]+)/revise$', path)
        if match:
            original_id = match.group(1)
            self._handle_revise(original_id, payload)
            return

        self._send_error(404, "Not Found")

    def _handle_evaluate(self, payload: dict):
        try:
            request = CustomEvaluationRequest(**payload)
        except ValidationError as e:
            self._send_error(422, f"Schema validation error: {str(e)}")
            return

        self._run_evaluation(request)

    def _handle_revise(self, original_id: str, payload: dict):
        evaluator = CustomEvaluator()
        original_eval = evaluator.get_evaluation(original_id)
        if not original_eval:
            self._send_error(404, "Original evaluation not found")
            return

        try:
            # We construct a new request combining original scenario/context with new evidence
            # We expect payload to contain an "evidence" array which gets appended
            new_evidence = payload.get("evidence", [])
            
            # We need the original request to rebuild correctly. The original evaluation only has the response.
            # But the response contains all evidence. We can just add the new evidence.
            # Wait, EvaluationResponse doesn't store scenario! 
            # If EvaluationResponse doesn't store scenario, we can't re-evaluate without it.
            # The saved JSON contains both "request" and "response".
            # We should probably load the raw JSON to get the original request.
            # Let's fix that. We can fetch it manually.
            pass
        except Exception:
            pass
            
        import os
        from proofsec.evaluator import get_project_root, _sanitize_id
        
        safe_id = _sanitize_id(original_id)
        file_path = get_project_root() / "custom_evaluations" / f"{safe_id}.json"
        
        if not file_path.exists():
            self._send_error(404, "Evaluation file missing")
            return
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        original_request = data.get("request", {})
        
        new_evidence = payload.get("evidence", [])
        if not isinstance(new_evidence, list):
            self._send_error(422, "evidence must be a list of strings")
            return
            
        combined_evidence = original_request.get("evidence", []) + new_evidence
        
        try:
            request = CustomEvaluationRequest(
                scenario=original_request.get("scenario", ""),
                context=original_request.get("context"),
                question=original_request.get("question"),
                evidence=combined_evidence,
                previous_evaluation_id=safe_id
            )
        except ValidationError as e:
            self._send_error(422, f"Schema validation error: {str(e)}")
            return
            
        self._run_evaluation(request)

    def _run_evaluation(self, request: CustomEvaluationRequest):
        evaluator = CustomEvaluator()
        try:
            eval_response = evaluator.evaluate(request)
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(eval_response.model_dump_json().encode('utf-8'))
        except ValueError as e:
            self._send_error(422, str(e))
        except RuntimeError as e:
            err_msg = str(e)
            if "AUTHENTICATION_ERROR" in err_msg:
                self._send_error(502, "Provider authentication failed.")
            elif "RATE_LIMIT" in err_msg:
                self._send_error(429, "Provider rate limit exceeded.")
            elif "TIMEOUT" in err_msg:
                self._send_error(504, "Provider timeout.")
            elif "CONFIGURATION_ERROR" in err_msg:
                self._send_error(503, "Provider not configured.")
            else:
                self._send_error(500, err_msg)
        except Exception as e:
            self._send_error(500, str(e))
