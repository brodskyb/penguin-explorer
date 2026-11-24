from html import escape
from urllib.parse import parse_qs, urlencode, urlsplit


def folders_by_size(directory: dict) -> list[tuple[str, dict]]:
    return sorted(
        directory["children"].items(),
        key=lambda item: item[1]["total_bytes"],
        reverse=True,
    )


def folder_at_path(snapshot: dict, parts: list[str]) -> dict:
    directory = snapshot["tree"]
    for name in parts:
        directory = directory["children"][name]
    return directory


def files_by_size(directory: dict) -> list[tuple[str, int]]:
    return sorted(
        directory["files"].items(),
        key=lambda item: item[1],
        reverse=True,
    )


def entries_by_size(directory: dict) -> list[tuple[str, str, int]]:
    entries = []
    for name, child in directory["children"].items():
        entries.append((name, "folder", child["total_bytes"]))
    for name, size in directory["files"].items():
        entries.append((name, "file", size))
    return sorted(entries, key=lambda entry: entry[2], reverse=True)


def breadcrumbs(parts: list[str]) -> list[tuple[str, list[str]]]:
    links = [("Root", [])]
    for depth, name in enumerate(parts, start=1):
        links.append((name, parts[:depth]))
    return links


def folder_url(parts: list[str]) -> str:
    query = urlencode({"part": parts}, doseq=True)
    return f"/?{query}" if query else "/"


def folder_parts_from_url(url: str) -> list[str]:
    query = urlsplit(url).query
    return parse_qs(query, keep_blank_values=True).get("part", [])


def folder_link(label: str, parts: list[str]) -> str:
    url = folder_url(parts)
    return f'<a href="{escape(url)}">{escape(label)}</a>'


def render_breadcrumbs(parts: list[str]) -> str:
    trail = breadcrumbs(parts)
    items = []
    for label, path in trail[:-1]:
        items.append(folder_link(label, path))
    current_label, _ = trail[-1]
    items.append(f'<span aria-current="page">{escape(current_label)}</span>')
    return '<nav aria-label="breadcrumb">' + ' / '.join(items) +'</nav>'


def render_entries(directory: dict, parts: list[str]) -> str:
    rows = []
    for name, kind, size in entries_by_size(directory):
        if kind == "folder":
            label = folder_link(name, parts + [name])
            if directory["children"][name]["errors"]:
                label += " (partial scan)"
        else:
            label = escape(name)
        rows.append(f"<li>{label} - {size:,} B</li>")
    if not rows:
        if directory["errors"]:
            return "<p>partial scan. No entries were recorded.</p>"
        return "<p>No files or folders were recorded.</p>"
    return "<ul>" + "".join(rows) + "</ul>"


def render_folder(snapshot: dict, parts: list[str]) -> str:
    directory = folder_at_path(snapshot, parts)
    completed_at = escape(snapshot["completed_at"])
    size_label = "Known logical size (partial scan)" if directory["errors"] else "Logical size"
    return (
        "<main>"
        f"{render_breadcrumbs(parts)}"
        f'<p>Last scanned <time datetime="{completed_at}">{completed_at}</time></p>'
        f"<p>{size_label}: {directory['total_bytes']:,} B</p>"
        f"{render_entries(directory, parts)}"
        "</main>"
    )


def render_page(snapshot: dict, parts: list[str]) -> str:
    name = parts[-1] if parts else "Root"
    return (
        '<!doctype html><html lang="en"><head>'
        '<meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f"<title>{escape(name)} | Penguin Explorer</title>"
        "</head><body>"
        f"{render_folder(snapshot, parts)}"
        "</body></html>"
    )