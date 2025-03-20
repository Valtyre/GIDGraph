from http.server import BaseHTTPRequestHandler
import json

class handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self):
        """Handle CORS preflight requests"""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # ✅ Allow frontend requests
        self.end_headers()
        self.wfile.write(json.dumps({"message": "Hello from GET request!"}).encode("utf-8"))

    def do_POST(self):
        content_length = int(self.headers["Content-Length"])
        body = json.loads(self.rfile.read(content_length))
        name = body.get("name", "world")

        self.send_response(200)
        self.send_header("Content-type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")  # ✅ Allow frontend requests
        self.end_headers()
        self.wfile.write(json.dumps({"message": f"Hello, {name}!"}).encode("utf-8"))
