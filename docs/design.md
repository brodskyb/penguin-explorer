# Penguin Explorer

**Working title:** Penguin Explorer  
**Publisher:** Brandon  
**Project:** A standalone, open-source, read-only storage explorer for Linux servers and homelabs.

Penguin Explorer is the working name for development. The public release name and license are open decisions. A possible companion transfer app can be named when it becomes its own project.

## Purpose

Penguin Explorer answers **“What’s taking up space on my server?”** from a browser. It brings the familiar experience of WinDirStat or DaisyDisk to a headless Linux machine: a folder list with recursive sizes, a clickable storage map, and a way to see when the numbers were last measured.

The first user is a homelab owner who can connect to a server over SSH and wants to explore storage visually. The motivating example is simple: open `/media`, see how much space **Movies** and **TV Shows** each occupy, then tap **TV Shows** to find the largest series. The same experience should work for a backup directory, a home folder, or any other readable Linux directory. Plex and seedboxes are useful test cases. Neither is required.

## First-release experience

1. Open Explorer on a phone or desktop and choose a saved location, such as **Home Pi** or **Remote server**.
2. See the configured scan root, when it was last scanned, and the filesystem’s available space when that figure can be determined.
3. Open a directory. Its children are sorted largest first. Each folder shows the total size of the files beneath it.
4. Tap a row or a block in the treemap to drill down. Both views follow the same path, and breadcrumbs make it easy to move back up. On a phone, the list comes first.
5. Refresh a folder or the whole location. The scan runs on the Explorer host and continues if the browser closes. When the user returns, they can see the result, progress, or reason it failed.

**First milestone:** From a saved scan, someone should be able to open a server, find its largest folder in three taps, and tell how recently it was measured.

## Version 1 scope

| Area | First-release behavior |
|---|---|
| **Sources** | Support local Linux directories and SSH-accessible Linux directories. Each location has a friendly name and an explicit scan root. Start with one local folder. Remote scanning uses existing SSH access and requires no Explorer installation on the remote host. |
| **Scanning** | Run background scans and persist completed results across service restarts. Keep the previous completed result browsable during a refresh. Expose progress or activity, completion time, and any errors. |
| **Browsing** | Provide a size-sorted directory list, recursive totals, breadcrumbs, and a linked treemap. Make paths, exact sizes, and navigation usable without color cues or hover interactions. |
| **Accuracy** | Label the measure used for folder sizes. Show whole-filesystem usage separately from the scanned tree. Flag partial results, skipped directories, and permission failures. |
| **Access** | Keep source access read-only and browsing scoped to configured roots. Verify SSH host identity and keep credentials out of scan records and logs. The initial deployment is intended for a home LAN or private VPN. |
| **Deployment** | Document a Docker Compose setup for ARM64 and x86-64. The first-run example mounts one directory read-only and stores Explorer’s settings and scan results separately. |

## What the size numbers mean

Use **logical file size** for the v1 folder list and treemap. This answers “How much file content is visible under this path?” Calculate both views from the same scan so their totals agree.

Hard links make this distinction important. A seedbox can list a 25 GB download in one directory and a hard link to it in a media library. Each path can show 25 GB while the two entries share the same disk blocks. Label the folder measure clearly and show filesystem used/free figures separately. Defer estimates of how much space deletion would reclaim.

By default, treat symlinks as links and stay on the selected filesystem during a scan. Users can add a mounted disk as another location. An empty directory should visibly differ from one Explorer could not read. If a remote account exposes filesystem-wide capacity but its personal quota is unknown, label the figure accordingly.

## Reuse by a future transfer app

A future companion could let users select remote files and queue verified copies onto local storage. Both products should work independently. Someone installing Explorer should get the complete read-only experience. Someone installing the transfer app should be able to browse a source without deploying an Explorer server first.

Start with an **internal storage library** that can answer four questions:

- What locations and roots can this connection read?
- What files and directories are under this path?
- What size information is available, how fresh is it, and is the scan complete?
- How much space is available on the destination filesystem, if known?

Explorer owns scan scheduling, saved results, navigation, and visualization. The transfer app could reuse the source connections and directory model, then own destination permissions, job scheduling, staging, retries, and verification. It would recheck the destination and available space when a transfer starts because a saved scan can be stale.

Keep the library in the Explorer repository for v1. Extract a shared package when the companion has a concrete need for it. A shared folder picker or an **Open in transfer app** action can follow once both applications are useful independently.

## Acceptance checks

- **Known totals:** Scan a test tree containing known file sizes, nested folders, and an empty directory. Verify that recursive totals and the treemap agree with the documented rules.
- **Honest results:** Include a hard link, a symlink loop, and an unreadable directory. The scan finishes, its counting behavior is predictable, and the unreadable directory is visibly marked.
- **Useful on a phone:** Open a saved scan of `lab-pi`, compare **Movies** with **TV Shows**, and find the largest show without initiating another scan.
- **Resilient scanning:** Start an SSH scan, close the browser, and return later. A successful result is available to browse. A failed refresh preserves the previous completed result and its timestamp.
- **Standalone installation:** A new user can launch Explorer with one read-only local mount, complete a scan, and browse it without configuring SSH, Plex, or a companion app.

## Build order

**Start with the local experience.** Scan one directory, save a snapshot, and make the recursive folder list usable on a phone. Add the treemap from the same snapshot. Then add SSH and test on a real remote tree, where latency, access restrictions, and incomplete capacity information matter.

File transfers, deletion, scheduled alerts, storage-growth history, and a plugin system can wait. The first demo is complete when someone opens Penguin Explorer, taps a server, and can explain where its space went.