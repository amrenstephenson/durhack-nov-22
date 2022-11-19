import importlib
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import sys
import json


SCRIPT_DIR = os.path.dirname(__file__)
visualisation_path = os.path.join(SCRIPT_DIR, "..", "visualisation", "visualisation.py")

loader = importlib.machinery.SourceFileLoader("visualisation", visualisation_path)
spec = importlib.util.spec_from_loader("visualisation", loader)
visualisation = importlib.util.module_from_spec(spec)
loader.exec_module(visualisation)


HOST_NAME = "0.0.0.0"
SERVER_PORT = 8080

ALLOWED_PATHS = ["dashboard.html", "api.html"]

vis = visualisation.Visualisation()


class DurhackServer(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path
        path = path[1:]  # Remove leading /
        path = path[:-1] if path.endswith("/") else path  # Remove trailing / (if there is one)
        if path == "api/currencies/num":
            self.good_response(str(len(vis.currency)))
        elif path == "api/currencies/raw":
            self.good_response(json.dumps(vis.currency))
        elif path == "":
            self.send_response(301)
            self.send_header("Location", "/dashboard")
            self.end_headers()
        else:
            path = path + ".html" if "." not in path else path  # Default to .html if no file type is given.

            if path in ALLOWED_PATHS:
                with open(os.path.join(SCRIPT_DIR, "public", path), "r") as f:
                    self.good_response(f.read())
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(f"<h1>ERROR 404</h1>{path} not found.", "utf-8"))

    def good_response(self, text):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(bytes(str(text), "utf-8"))


if __name__ == "__main__":
    durhack_server = HTTPServer((HOST_NAME, SERVER_PORT), DurhackServer)
    print(f"Server started at http://{HOST_NAME}:{SERVER_PORT}")

    try:
        durhack_server.serve_forever()
    except KeyboardInterrupt:
        pass

    durhack_server.server_close()
    print("Server stopped.")
