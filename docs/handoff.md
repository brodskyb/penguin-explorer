# Penguin Explorer handoff

## Implemented

`direct_file_bytes(directory)` in `scanner.py` totals the logical bytes of regular files directly inside a directory. It uses helpers for listing children, identifying regular files, and reading their sizes.

## Verified on macOS

- The size helper matched an independent `wc -c` count for the design brief.
- Listing `docs/` returned the same paths as an independent directory listing.
- In a temporary directory, the regular-file check returned true for a file and false for both a directory and a symbolic link to that file.
- The direct total was 0 bytes for an empty directory and 8 bytes for two files of 3 and 5 bytes alongside a symlink and a nested 100-byte file. Adding a hard link to the 3-byte file raised the total to 11 bytes.

The [contributor guide](../AGENTS.md#checking-changes) includes a repeatable check. Linux and SSH verification are pending.

## Next step

Next, identify child directories without following symlinks. This prepares for recursive totals within the selected filesystem. The [design brief](design.md) defines how recursion, saved snapshots, and browsing should behave.
