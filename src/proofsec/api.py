import json
import sys
import re
import os
import time
import uuid
from http.server import BaseHTTPRequestHandler
from urllib.parse import urlparse

from proofsec.schemas import CustomEvaluationRequest, CUSTOM_EVALUATION_VERSION
from proofsec.evaluator import CustomEvaluator
from proofsec.providers import get_provider
from proofsec.compare import CompareEngine
from pydantic import ValidationError

RATE_LIMIT_WINDOW = 60
RATE_LIMIT_MAX_REQUESTS = 100
_rate_limits = {}

class ProofSecAPIHandler(BaseHTTPRequestHandler):
    
    def _send_error(self, code, message):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def _authenticate_request(self):
        """Authentication middleware abstraction."""
        if os.environ.get('PROOFSEC_REQUIRE_AUTH') != '1':
            return True
            
        auth_header = self.headers.get('Authorization')
        if not auth_header or not auth_header.startswith("Bearer "):
            self._send_error(401, "Authentication required")
            return False
            
        # Token validation logic would go here for a hosted product
        # For now, it's just a structural placeholder.
        token = auth_header.split(" ")[1]
        if token != os.environ.get('PROOFSEC_API_KEY', 'default_dev_token'):
            self._send_error(403, "Invalid API Key")
            return False
            
        return True

    def _check_rate_limit(self):
        client_ip = self.client_address[0]
        current_time = time.time()
        
        if client_ip not in _rate_limits:
            _rate_limits[client_ip] = []
            
        requests = _rate_limits[client_ip]
        requests = [req_time for req_time in requests if current_time - req_time < RATE_LIMIT_WINDOW]
        
        if len(requests) >= RATE_LIMIT_MAX_REQUESTS:
            self._send_error(429, "Rate limit exceeded. Try again later.")
            return False
            
        requests.append(current_time)
        _rate_limits[client_ip] = requests
        return True

    def do_GET(self):
        if not self._check_rate_limit():
            return
            
        if not self._authenticate_request():
            return
        
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        
        if not path.startswith('/api/'):
            if '.' not in path.split('/')[-1]:
                return self._serve_static('/index.html')
            return self._serve_static(path)

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

        if path == '/api/v1/evaluations':
            evaluator = CustomEvaluator()
            records = evaluator.store.list_all()
            history = []
            for r in records:
                history.append({
                    "evaluation_id": r.response.evaluation_id,
                    "classification": r.response.classification,
                    "evidence_state": r.response.evidence_state,
                    "summary": r.response.summary,
                    "created_at": r.response.created_at
                })
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"evaluations": history}).encode('utf-8'))
            return

        match = re.match(r'^/api/v1/evaluations/([a-zA-Z0-9_\-]+)$', path)
        if match:
            eval_id = match.group(1)
            evaluator = CustomEvaluator()
            record = evaluator.store.get(eval_id)
            if not record:
                self._send_error(404, "Evaluation not found")
                return
                
            metrics = CompareEngine.calculate_metrics(record.request, record.response)
                
            resp_dict = record.response.model_dump()
            resp_dict["metrics"] = metrics
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp_dict).encode('utf-8'))
            return

        match = re.match(r'^/api/v1/evaluations/([a-zA-Z0-9_\-]+)/revisions$', path)
        if match:
            eval_id = match.group(1)
            evaluator = CustomEvaluator()
            revisions = []
            current_id = eval_id
            
            while current_id:
                rec = evaluator.store.get(current_id)
                if not rec:
                    break
                revisions.append(rec.response.model_dump())
                current_id = rec.response.previous_evaluation_id
                
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"revisions": revisions}).encode('utf-8'))
            return

        if path == '/api/v1/benchmark':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "version": "v0.2",
                "tasks": 110,
                "categories": ["authentication", "authorization", "ssrf", "sqli", "idor", "xss", "business_logic", "csrf", "jwt", "rate_limiting", "security_headers", "sessions", "information_disclosure", "terminology_traps"]
            }).encode('utf-8'))
            return

        if path == '/api/v1/benchmark/hash':
            from proofsec.research import calculate_dataset_hash
            from proofsec.evaluator import get_project_root
            root = get_project_root()
            tasks_dir = root / "tasks"
            current_hash = calculate_dataset_hash(str(tasks_dir))
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"hash": current_hash}).encode('utf-8'))
            return
            
        if path == '/api/v1/research/metrics':
            from proofsec.research import get_research_status
            status = get_research_status()
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(status).encode('utf-8'))
            return

        self._send_error(404, "Not Found")

    def _serve_static(self, path):
        import mimetypes
        from proofsec.evaluator import get_project_root
        
        if path == '/':
            path = '/index.html'
            
        # Security: Prevent path traversal
        normalized_path = os.path.normpath(path).lstrip('\\/')
        file_path = get_project_root() / "web" / normalized_path
        
        if not str(file_path.resolve()).startswith(str((get_project_root() / "web").resolve())):
            self.send_response(403)
            self.end_headers()
            return
            
        if not file_path.is_file():
            self.send_response(404)
            self.end_headers()
            return
            
        mime_type, _ = mimetypes.guess_type(str(file_path))
        if not mime_type:
            mime_type = 'application/octet-stream'
            
        with open(file_path, 'rb') as f:
            content = f.read()
            
        self.send_response(200)
        self.send_header('Content-Type', mime_type)
        self.end_headers()
        self.wfile.write(content)


    def do_POST(self):
        if not self._check_rate_limit():
            return
            
        if not self._authenticate_request():
            return
            
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
            
        match = re.match(r'^/api/v1/evaluations/([a-zA-Z0-9_\-]+)/compare$', path)
        if match:
            eval_id = match.group(1)
            self._handle_compare(eval_id, payload)
            return

        self._send_error(404, "Not Found")

    def _handle_evaluate(self, payload: dict):
        provider = payload.get("provider")
        try:
            # We don't want to pass 'provider' to CustomEvaluationRequest if it's not a valid field, 
            # so we pop it. Or just rely on Pydantic to ignore it if extra="ignore".
            # To be safe:
            if "provider" in payload:
                payload = {k: v for k, v in payload.items() if k != "provider"}
            request = CustomEvaluationRequest(**payload)
        except ValidationError as e:
            self._send_error(422, f"Schema validation error: {str(e)}")
            return

        self._run_evaluation(request, provider_name=provider)

    def _handle_revise(self, original_id: str, payload: dict):
        evaluator = CustomEvaluator()
        record = evaluator.store.get(original_id)
        if not record:
            self._send_error(404, "Original evaluation not found")
            return

        original_request = record.request
        new_evidence = payload.get("evidence", [])
        if not isinstance(new_evidence, list):
            self._send_error(422, "evidence must be a list of strings")
            return
            
        combined_evidence = original_request.evidence + new_evidence
        
        try:
            request = CustomEvaluationRequest(
                scenario=original_request.scenario,
                context=original_request.context,
                question=original_request.question,
                evidence=combined_evidence,
                previous_evaluation_id=original_id,
                expected_classification=original_request.expected_classification,
                expected_evidence_state=original_request.expected_evidence_state,
                expected_decisive_fact=original_request.expected_decisive_fact
            )
        except ValidationError as e:
            self._send_error(422, f"Schema validation error: {str(e)}")
            return
            
        self._run_evaluation(request)
        
    def _handle_compare(self, eval_id: str, payload: dict):
        target_id = payload.get("target_id")
        if not target_id:
            self._send_error(422, "target_id is required")
            return
            
        evaluator = CustomEvaluator()
        record_a = evaluator.store.get(eval_id)
        record_b = evaluator.store.get(target_id)
        
        if not record_a or not record_b:
            self._send_error(404, "One or both evaluations not found")
            return
            
        comparison = CompareEngine.compare_evaluations(record_a.response, record_b.response)
        
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps(comparison).encode('utf-8'))

    def _run_evaluation(self, request: CustomEvaluationRequest, provider_name: Optional[str] = None):
        if provider_name:
            provider = get_provider(provider_name)
            evaluator = CustomEvaluator(provider=provider)
        else:
            evaluator = CustomEvaluator()
            
        try:
            eval_response = evaluator.evaluate(request)
            
            metrics = CompareEngine.calculate_metrics(request, eval_response)
            
            resp_dict = eval_response.model_dump()
            resp_dict["metrics"] = metrics
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(resp_dict).encode('utf-8'))
        except ValueError as e:
            self._send_error(422, str(e))
        except Exception as e:
            from proofsec.evaluator import ProviderError
            if isinstance(e, ProviderError):
                code_map = {
                    "AUTHENTICATION_ERROR": 502,
                    "RATE_LIMIT": 429,
                    "TIMEOUT": 504,
                    "CONFIGURATION_ERROR": 503
                }
                http_code = code_map.get(e.status, 502)
                
                resp = {
                    "evaluation_id": f"eval-{uuid.uuid4().hex[:12]}",
                    "status": "failed",
                    "error": {
                        "code": e.status,
                        "message": e.message if e.message else f"{e.provider} error",
                        "provider": e.provider,
                        "recoverable": e.status in ["AUTHENTICATION_ERROR", "RATE_LIMIT", "CONFIGURATION_ERROR"],
                        "action": f"Run `proofsec auth {e.provider}`" if e.status == "AUTHENTICATION_ERROR" else "Check provider configuration"
                    }
                }
                self.send_response(http_code)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
            else:
                import logging
                # Safe structured logging
                logging.error(f"evaluation_id=unknown provider=unknown status=INTERNAL_ERROR type={type(e).__name__}")
                
                resp = {
                    "status": "failed",
                    "error": {
                        "code": "INTERNAL_ERROR",
                        "message": "The evaluation could not be completed.",
                        "recoverable": True
                    }
                }
                self.send_response(500)
                self.send_header('Content-Type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps(resp).encode('utf-8'))
