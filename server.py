from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

from browse import folder_parts_from_url, render_page


def page_for_request(snapshot: dict, target: str) -> tuple[int, str]:
    if urlsplit(target).path != "/":
        return 404, "<p>Page not found.</p>"
    parts = folder_parts_from_url(target)
    try:
        page = render_page(snapshot, parts)
    except KeyError:
        return 404, "<p>Folder not found in this snapshot.</p>"
    return 200, page


def serve_snapshot(snapshot: dict, port: int = 8000) -> None:
    class ExplorerHandler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            status, page = page_for_request(snapshot, self.path)
            body = page.encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    with HTTPServer(("127.0.0.1", port), ExplorerHandler) as server:
        server.serve_forever()