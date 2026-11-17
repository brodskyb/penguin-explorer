# Penguin Explorer contributor guide

Start with [the design brief](docs/design.md) for product requirements and [the handoff](docs/handoff.md) for implemented behavior and outstanding work. The initial Python helpers live in `scanner.py`. Build the local scanner first, followed by saved snapshots, mobile browsing, the treemap, and SSH sources.

## Scanning rules

- Scan read-only beneath the configured root. Treat symlinks as links and stay on the selected filesystem.
- Sum the logical byte size of regular files at each visible path. Two hard links to one file each contribute its full size. Report filesystem capacity separately.
- Preserve the distinction between an empty directory and an unreadable one. Mark skipped entries and partial totals.
- Derive the directory list and treemap from the same completed snapshot. Keep that snapshot browsable during a refresh and preserve its timestamp if the refresh fails.
- Verify SSH host identity for remote scans. Keep credentials and private keys out of tracked files, logs, and scan records.

## Checking changes

For a quick check of the current helpers, run this from the project root with Python 3. It measures a known file, lists a directory, and checks that a symbolic link to a file is classified separately.

```sh
python3 -B - <<'PY'
from pathlib import Path
from tempfile import TemporaryDirectory
from scanner import is_regular_file, list_children, logical_file_size

with TemporaryDirectory() as tmp:
    root = Path(tmp)
    sample = root / "sample"
    sample.write_bytes(b"abc")
    link = root / "link"
    link.symlink_to(sample)

    assert logical_file_size(sample) == 3
    assert set(list_children(root)) == {sample, link}
    assert is_regular_file(sample)
    assert not is_regular_file(root)
    assert not is_regular_file(link)
print("Scanner helper checks passed")
PY
```

When implementing recursive totals, extend verification to nested and empty directories, hard links, symlink loops, and permission failures. The [acceptance checks](docs/design.md#acceptance-checks) cover snapshot recovery, phone navigation, SSH, and installation as those features become available.
