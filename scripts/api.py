import json
import sys
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Setup paths
root = Path(__file__).parent.parent
sys.path.insert(0, str(root))

from proofsec.schemas import CustomEvaluationRequest
from proofsec.evaluator import CustomEvaluator
from pydantic import ValidationError

class ProofSecAPIHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path != '/api/v1/evaluate':
            self.send_response(404)
            self.end_headers()
            return

        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            payload = json.loads(post_data)
            request = CustomEvaluationRequest(**payload)
        except json.JSONDecodeError:
            self._send_error(400, "Invalid JSON payload")
            return
        except ValidationError as e:
            self._send_error(422, f"Schema validation error: {str(e)}")
            return

        evaluator = CustomEvaluator()

        try:
            eval_response = evaluator.evaluate(request)
            response_body = eval_response.model_dump()

            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response_body).encode('utf-8'))
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
                self._send_error(503, "Provider unavailable.")
        except Exception:
            self._send_error(500, "Internal server error")

    def _send_error(self, code: int, message: str):
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({"error": message}).encode('utf-8'))

    def log_message(self, format, *args):
        """Suppress default stderr logging in tests; override for production."""
        pass

def run_server(port=8080):
    server_address = ('', port)
    httpd = HTTPServer(server_address, ProofSecAPIHandler)
    print(f"ProofSec local API running on http://localhost:{port}")
    print("POST /api/v1/evaluate")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server.")
        httpd.server_close()

if __name__ == '__main__':
    run_server()
