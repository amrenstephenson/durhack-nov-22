# Python 3 server example
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST_NAME = "0.0.0.0"
SERVER_PORT = 8080


class DurhackServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api" or self.path.startswith("/api/"):
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes(f"It's the API!", "utf-8"))
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
