import argparse
import ipaddress
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from ip_url_tool import classify_url_type, resolve_ip_url, resolve_url

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
MAX_REQUEST_BYTES = 4096


def lookup_target(value: str) -> dict[str, Any]:
    """Resolve a URL/domain or return reverse-DNS details for an IP address."""
    target = value.strip()
    if not target:
        return {
            "url": target,
            "host": None,
            "ips": [],
            "type": "Unknown",
            "status": "invalid",
        }

    try:
        ipaddress.ip_address(target)
    except ValueError:
        return resolve_url(target)

    reverse_result = resolve_ip_url(target)
    hostname = reverse_result["url"]
    return {
        "url": target,
        "host": hostname,
        "ips": [target],
        "type": classify_url_type(hostname) if hostname else "IP address",
        "status": reverse_result["status"],
    }


class URLIDHandler(BaseHTTPRequestHandler):
    def _send_bytes(self, status: int, content: bytes, content_type: str) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; style-src 'self'; script-src 'self'; connect-src 'self'; img-src 'self' data:")
        self.end_headers()
        self.wfile.write(content)

    def _send_json(self, status: int, data: dict[str, Any]) -> None:
        content = json.dumps(data).encode("utf-8")
        self._send_bytes(status, content, "application/json; charset=utf-8")

    def do_GET(self) -> None:
        route = urlparse(self.path).path
        if route == "/api/health":
            self._send_json(200, {"status": "ok"})
            return

        static_files = {
            "/": ("index.html", "text/html; charset=utf-8"),
            "/styles.css": ("styles.css", "text/css; charset=utf-8"),
            "/app.js": ("app.js", "text/javascript; charset=utf-8"),
        }
        asset = static_files.get(route)
        if asset is None:
            self._send_json(404, {"error": "Not found"})
            return

        filename, content_type = asset
        try:
            content = (STATIC_DIR / filename).read_bytes()
        except OSError:
            self._send_json(500, {"error": "Web asset unavailable"})
            return
        self._send_bytes(200, content, content_type)

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/api/lookup":
            self._send_json(404, {"error": "Not found"})
            return

        try:
            request_size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            request_size = 0
        if request_size <= 0 or request_size > MAX_REQUEST_BYTES:
            self._send_json(400, {"error": "Request must contain a short JSON target"})
            return

        try:
            payload = json.loads(self.rfile.read(request_size))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Invalid JSON"})
            return
        if not isinstance(payload, dict) or not isinstance(payload.get("target"), str):
            self._send_json(400, {"error": "Provide a URL, domain, or IP address"})
            return

        self._send_json(200, lookup_target(payload["target"]))

    def log_message(self, format: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format % args}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the URLID web interface.")
    parser.add_argument("--host", default="127.0.0.1", help="Interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8000, help="Port to listen on (default: 8000)")
    args = parser.parse_args()

    server = ThreadingHTTPServer((args.host, args.port), URLIDHandler)
    print(f"URLID is ready at http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping URLID web server")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
