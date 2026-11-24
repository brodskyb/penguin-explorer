from argparse import ArgumentParser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from browse import folder_parts_from_url, render_page
from snapshot import load_snapshot


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


if __name__ == "__main__":
    parser = ArgumentParser(description="Browse a saved Penguin Explorer snapshot.")
    parser.add_argument("snapshot", type=Path, help="Path to the saved JSON snapshot")
    args = parser.parse_args()
    try:
        snapshot = load_snapshot(args.snapshot)
    except (OSError, ValueError) as error:
        parser.error(str(error))
    serve_snapshot(snapshot)