from http.server import BaseHTTPRequestHandler, HTTPServer
import os


HOST_NAME = "0.0.0.0"
SERVER_PORT = 8080

ALLOWED_PATHS = ["dashboard.html"]


class DurhackServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api" or self.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(f"It's the API!", "utf-8"))
        elif self.path == "/":
            self.send_response(301)
            self.send_header('Location', '/dashboard')
            self.end_headers()
        else:
            self.path = self.path[1:]  # Remove leading /
            self.path = self.path[:-1] if self.path.endswith("/") else self.path  # Remove trailing / (if there is one)
            self.path = self.path + ".html" if "." not in self.path else self.path  # Default to .html if no file type is given.

            if self.path in ALLOWED_PATHS:
                with open(os.path.join(os.path.dirname(__file__), "public", self.path), "r") as f:
                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(bytes(f.read(), "utf-8"))
            else:
                self.send_response(404)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes(f"<h1>ERROR 404</h1>{self.path} not found.", "utf-8"))


if __name__ == "__main__":
    durhack_server = HTTPServer((HOST_NAME, SERVER_PORT), DurhackServer)
    print(f"Server started at http://{HOST_NAME}:{SERVER_PORT}")

    try:
        durhack_server.serve_forever()
    except KeyboardInterrupt:
        pass

    durhack_server.server_close()
    print("Server stopped.")
