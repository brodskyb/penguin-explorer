# Penguin Explorer handoff

## Implemented

`direct_file_bytes(directory)` in `scanner.py` totals the logical bytes of regular files directly inside a directory on the same filesystem. It uses helpers for listing children, comparing filesystem identifiers, identifying regular files, and reading their sizes.

`is_directory(path)` identifies directory entries without following symlinks.

`same_filesystem(path, root)` compares the filesystem identifiers of two entries.

`recursive_file_bytes(directory)` adds direct file totals from child directories on the same filesystem. It skips symlink entries and rejects a file or symlink supplied as the starting directory.

`ScanResult` holds a byte total and a list of scan errors. `list_children_for_scan()` records directory-listing errors in that result.

`scan_directory()` records each regular file's name and logical size in its containing directory. It retains child directory results by name, adds their known bytes to the parent total, and propagates their errors to the parent.

`create_snapshot(root)` in `snapshot.py` packages the scanned tree with the absolute root path and UTC completion time.

`save_snapshot(snapshot, destination)` writes JSON to a temporary file in the destination's parent directory, then replaces the destination once the write completes.

`load_snapshot(path)` reads the saved JSON for browsing.

`browse.py` lists saved entries largest first, builds breadcrumb paths, and converts between ordered folder names and browser URLs. `folder_at_path()` looks up those names in the snapshot tree.

## Verified on macOS

- The size helper matched an independent `wc -c` count for the design brief.
- Listing `docs/` returned the same paths as an independent directory listing.
- In a temporary directory, the regular-file check returned true for a file and false for both a directory and a symbolic link to that file.
- The direct total was 0 bytes for an empty directory and 8 bytes for two files of 3 and 5 bytes alongside a symlink and a nested 100-byte file. Adding a hard link to the 3-byte file raised the total to 11 bytes.
- The directory helper returned true for a directory and false for a regular file and a symbolic link to a directory.
- The filesystem helper returned true for a file and child directory on the temporary test root's filesystem, and false for `/dev`, whose filesystem identifier differed on the Mac.
- After applying the filesystem check to direct totals, the 0-, 8-, and 11-byte cases still passed. Simulating a different filesystem identifier for an additional 1,000-byte regular file excluded that file from the total. This exclusion check used mocked metadata.
- Recursive totals were 0 bytes for an empty tree, 108 bytes for the nested example with symlink loops, 125 bytes after adding a deeper 17-byte file, and 128 bytes after adding a hard link to the 3-byte file. A file or symlink supplied as the starting directory raised `NotADirectoryError`.
- Simulating a different filesystem identifier for the nested directory excluded its subtree, leaving 11 bytes at the root. An actual unreadable directory caused the scan to raise `PermissionError`.
- The reported terminal scan of `docs/` returned 9,828 bytes. An independent `wc -c` check matched that result before this handoff update, with 7,068 bytes in the design brief and 2,760 bytes in the handoff.
- Two new `ScanResult` instances each started at zero bytes with an empty list. Appending an error to the first left the second list empty.
- An empty directory returned no children or errors. A directory with read access removed returned no children and recorded one permission error naming the directory. Listing a readable sibling afterward returned its file and preserved the earlier error.
- With 3 bytes at the root, 5 in a readable child, and 100 in an unreadable sibling, `scan_directory()` returned 8 known bytes and one permission error naming the sibling. Restoring access gave 108 bytes and zero errors. The tree included a symlink back to the root.
- Named child results distinguished an empty folder (0 bytes, no errors) from a blocked folder (0 known bytes, one permission error). A readable sibling retained its nested folder's 5 bytes. The root included another 3 bytes directly and reported the blocked folder's error once.
- Two files named `sample` were recorded under their respective directories with sizes of 3 and 5 bytes. A zero-byte file remained visible, a symlink was skipped, and the root total was 8 bytes.
- The corrected `create_snapshot` import worked. A JSON round trip preserved the root, UTC timestamp, nested file entries, and 8-byte total.
- An 8-byte tree reopened from the saved JSON file. A refresh with a value that JSON could not encode preserved the previous file byte for byte, including its completion time. A subsequent successful refresh reopened with a 12-byte total. Only the saved snapshot remained in the destination directory.
- After moving the source folder and changing a file, `load_snapshot()` returned the original root, completion time, 8-byte total, and nested 5-byte file.
- After moving a test source and reopening its snapshot, the root listed TV Shows (15 bytes), Movies (9), and Empty (0). TV Shows listed Series B (12) before Series A (3), and browsing Empty returned an empty list.
- On a reopened snapshot with the source moved, `folder_at_path()` returned the 24-byte root for an empty path and the 12-byte Series B folder for a two-part path. A missing child raised `KeyError` with the missing name.
- After the source was moved, `files_by_size()` listed the selected folder's files at 12, 3, and 0 bytes in descending order. A folder containing only a subfolder returned an empty file list.
- With the source moved, `entries_by_size()` listed a 20-byte file, a 12-byte folder, and a 3-byte file in that order from a reopened snapshot. Its verified return annotation is `list[tuple[str, str, int]]` for name, kind, and logical byte count.
- On a reopened snapshot with its source moved, the breadcrumbs for TV Shows / Series B resolved to Root (24 bytes), TV Shows (15), and Series B (12). At the root the only breadcrumb was Root.
- `folder_url([])` returned `/`. Decoding generated links with Python’s URL parser recovered the original folder names in order, including `TV Shows`, `Sci-Fi & Fantasy`, `C++`, `100%`, and `Café #1`.
- After moving the source and reopening the JSON, `folder_parts_from_url()` and `folder_at_path()` resolved `/` to the 20-byte root and the two-part URL for TV Shows / Sci-Fi & Fantasy to the 12-byte folder containing `episode`.
- Python’s HTML parser read one link from `folder_link()` with the exact label `Shows <2026> & More`. After moving the source, the link resolved in the reopened snapshot to the folder containing the 7-byte `episode` file. The root link resolved to the 10-byte root.
- `render_breadcrumbs()` marked Root as current at the root. In Root / Media / Shows it marked Shows as current, and its two parent links resolved to the 10-byte root and 7-byte Media folder in a reopened snapshot after the source moved.
- After moving the source, `render_entries()` showed a 1,024-byte file, a 12-byte folder, and a 3-byte file in descending order. The TV & Film link resolved to its saved 12-byte episode. Of two 0-byte folders, only the one denied read access during the scan showed “partial scan” in its parent row.
- Opening three 0-byte folders from a reopened snapshot produced distinct results. The empty folder reported no recorded files or folders, the unreadable folder reported a partial scan, and the folder containing `marker.txt` listed the file at 0 B.
- After moving the source, `render_folder()` showed 15 known bytes at Root, 12 bytes at Root / TV & Film, and 0 known bytes at Root / Blocked. The blocked folder and its parent showed partial totals. All three views displayed the saved completion time.
- In a reopened snapshot, Python’s HTML parser found the expected titles for Root and TV & Film. Both pages declared UTF-8 and one viewport with `width=device-width, initial-scale=1`. A phone layout check is pending.
- With the source moved, `serve_snapshot()` served reopened JSON over HTTP on `127.0.0.1`. The 10-byte root and its Café & Film link returned 200, the child listed the saved 7-byte episode, and both pages showed the saved scan time. A missing folder and an unknown route returned distinct 404 messages. All four responses declared UTF-8 HTML and the exact body length in bytes. The temporary server was stopped.

The [contributor guide](../AGENTS.md#checking-changes) includes a repeatable check. Linux and SSH verification are pending.

## Next step

Add a command-line entry point that opens a saved snapshot by filename and starts the local server. A snapshot missing `completed_at` currently produces a misleading folder-missing 404. Distinguishing invalid snapshots and handling deep trees are pending. The [design brief](design.md) defines how browsing should behave.
