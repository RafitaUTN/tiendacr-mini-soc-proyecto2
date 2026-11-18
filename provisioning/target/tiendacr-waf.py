#!/usr/bin/env python3
"""Lab reverse proxy blocking common SQLi, traversal, and XSS probes."""
from http.client import HTTPConnection
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote_plus
import logging
import re

UPSTREAM_HOST = "127.0.0.1"
UPSTREAM_PORT = 3001
LISTEN_HOST = "10.10.10.10"
LISTEN_PORT = 3000
SQLI = re.compile(
    r"(?:['\"]\s*(?:or|and)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+"
    r"|\bunion\s+(?:all\s+)?select\b|\b(?:sleep|benchmark)\s*\()",
    re.IGNORECASE,
)
XSS = re.compile(r"<\s*script\b|javascript\s*:|\bon\w+\s*=", re.IGNORECASE)
HOP_HEADERS = {"connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
               "te", "trailers", "transfer-encoding", "upgrade"}

logging.basicConfig(level=logging.INFO, format="%(asctime)s tiendacr-waf %(message)s")


class WAFProxy(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def _blocked(self):
        decoded = unquote_plus(unquote_plus(self.path))
        path = decoded.split("?", 1)[0]
        reason = None
        if any(part == ".." for part in path.split("/")):
            reason = "path-traversal"
        elif SQLI.search(decoded):
            reason = "sql-injection"
        elif XSS.search(decoded):
            reason = "xss"
        if reason:
            logging.warning("blocked reason=%s src=%s", reason, self.client_address[0])
            body = ("Request blocked by TiendaCR lab WAF: " + reason + "\n").encode()
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.send_header("X-TiendaCR-WAF", "blocked")
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(body)
            self.close_connection = True
            return True
        return False

    def _proxy(self):
        if self._blocked():
            return
        length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items()
                   if k.lower() not in HOP_HEADERS | {"host", "content-length"}}
        if body is not None:
            headers["Content-Length"] = str(len(body))
        upstream = HTTPConnection(UPSTREAM_HOST, UPSTREAM_PORT, timeout=15)
        try:
            upstream.request(self.command, self.path, body=body, headers=headers)
            response = upstream.getresponse()
            payload = response.read()
            self.send_response(response.status, response.reason)
            for key, value in response.getheaders():
                if key.lower() not in HOP_HEADERS | {"content-length", "server", "date"}:
                    self.send_header(key, value)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            if self.command != "HEAD":
                self.wfile.write(payload)
            self.close_connection = True
        except Exception as error:
            logging.error("upstream-error=%s", type(error).__name__)
            payload = b"TiendaCR lab WAF upstream unavailable\n"
            self.send_response(502)
            self.send_header("Content-Length", str(len(payload)))
            self.send_header("Connection", "close")
            self.end_headers()
            self.wfile.write(payload)
            self.close_connection = True
        finally:
            upstream.close()

    do_GET = _proxy
    do_HEAD = _proxy
    do_POST = _proxy
    do_PUT = _proxy
    do_PATCH = _proxy
    do_DELETE = _proxy
    do_OPTIONS = _proxy

    def log_message(self, fmt, *args):
        logging.info("src=%s %s", self.client_address[0], fmt % args)


if __name__ == "__main__":
    ThreadingHTTPServer((LISTEN_HOST, LISTEN_PORT), WAFProxy).serve_forever()
