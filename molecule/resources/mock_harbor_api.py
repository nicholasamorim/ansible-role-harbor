#!/usr/bin/env python3
import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, HTTPServer


class HarborHandler(BaseHTTPRequestHandler):
    projects = set()
    users = set()
    log_path = None

    def _write_log(self, method, path, status, body):
        entry = {
            "method": method,
            "path": path,
            "status": status,
            "body": body,
        }
        with open(self.log_path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(entry, separators=(",", ":")) + "\n")

    def _read_body(self):
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length == 0:
            return None
        raw_body = self.rfile.read(content_length).decode("utf-8")
        try:
            return json.loads(raw_body)
        except json.JSONDecodeError:
            return raw_body

    def _send_json(self, status, payload):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._write_log("GET", self.path, 200, None)
        if self.path.startswith("/api/v2.0/projects"):
            payload = [{"name": name} for name in sorted(self.projects)]
            self._send_json(200, payload)
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self):
        body = self._read_body()
        if self.path == "/api/v2.0/projects":
            project_name = body.get("project_name")
            status = 409 if project_name in self.projects else 201
            if status == 201:
                self.projects.add(project_name)
            self._write_log("POST", self.path, status, body)
            self._send_json(status, {"project_name": project_name})
            return
        if self.path == "/api/v2.0/users":
            username = body.get("username")
            status = 409 if username in self.users else 201
            if status == 201:
                self.users.add(username)
            self._write_log("POST", self.path, status, body)
            self._send_json(status, {"username": username})
            return
        self._write_log("POST", self.path, 404, body)
        self._send_json(404, {"error": "not found"})

    def log_message(self, format, *args):
        return


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, required=True)
    parser.add_argument("--log", required=True)
    args = parser.parse_args()

    os.makedirs(os.path.dirname(args.log), exist_ok=True)
    HarborHandler.log_path = args.log

    server = HTTPServer(("127.0.0.1", args.port), HarborHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
