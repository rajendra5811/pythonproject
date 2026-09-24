import json
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

USERS = { 1: {"id": 1, "name": "ada", "active": True}, 2: {"id": 2, "name": "bob", "active": False} }

class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/users":
            active = parse_qs(url.query).get("active")
            users = list(USERS.values())
            if active:
                users = [u for u in users if u["active"] == (active[0].lower() == "true")]
            return self.send_json(200, users)
        if url.path.startswith("/users/"):
            user = USERS.get(int(url.path.rsplit("/", 1)[1]))
            return self.send_json(200, user) if user else self.send_json(404, {"error": "User not found"})
        if url.path == "/delay":
            time.sleep(0.2)
            return self.send_json(200, {"waited": 0.2})
        if url.path == "/slow":
            time.sleep(2)
            return self.send_json(200, {})
        if url.path == "/boom":
            return self.send_json(503, {"error": "try again later"})
        self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data = json.loads(self.rfile.read(length) or b"{}")
        if "name" not in data:
            return self.send_json(400, {"error": "Missing name"})
        new_id = max(USERS.keys()) + 1
        USERS[new_id] = {"id": new_id, "name": data["name"], "active": True}
        self.send_json(201, USERS[new_id])

class Server(ThreadingHTTPServer):
    request_queue_size = 32

def start_server():
    server = Server(("127.0.0.1", 0), Handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_port}"
