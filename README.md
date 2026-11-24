# Optimizer Pro — Command Center

![Python](https://img.shields.io/badge/python-3.9%2B-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![License](https://img.shields.io/badge/license-MIT-green)

A Windows desktop PC-cleaner / system-maintenance daemon (CustomTkinter GUI) with a live performance dashboard, one-click junk/cache cleanup, a lightweight auto RAM guard, and a USB "shield" that watches for newly inserted drives carrying suspicious executables.

## Features

- **Live dashboard** — real-time CPU load and RAM usage, plus a running count of items cleaned, refreshed every second.
- **One-click Purge** — deletes temp files and folders from `C:\Windows\Temp`, your user `AppData\Local\Temp`, `C:\Windows\Prefetch`, and the Chrome/Edge disk cache folders.
- **Auto RAM Guard** — when system RAM usage exceeds 85%, automatically terminates the single process currently using the most memory (excluding core OS processes like `System`, `svchost.exe`, `explorer.exe`).
- **USB Shield** — uses WMI to watch for newly mounted drives/volumes; when one appears, it scans the drive's root folder for executable-ish files (`.exe`, `.bat`, `.vbs`, `.cmd`, `.inf`, `.lnk`) and raises a warning popup + log entry if any are found.
- **Unattended modes** for scheduling via Task Scheduler:
  - `--silent-purge` — runs a full cleanup with no UI, meant to be scheduled periodically (e.g. every 12 hours).
  - `--startup-report` — runs a cleanup at login and shows a short "optimization report" dialog.

## ⚠️ Things to know before running this

- **Auto RAM Guard force-closes applications without saving your work.** If something other than a browser/background process happens to be the top memory consumer when RAM crosses 85%, it will be killed outright — this can mean lost unsaved work in whatever app that is. Treat this as an aggressive/experimental feature, not a safe auto-save.
- **Deep Purge permanently deletes files** from the temp/prefetch/cache folders listed above, with no undo and no confirmation prompt per file. It fails silently on files that are locked/in-use, but anything it *can* delete, it will.
- Several of its targets (`C:\Windows\Temp`, `C:\Windows\Prefetch`) require the app to run **as Administrator** to actually clean them; otherwise those steps just silently do nothing.
- This is a personal/portfolio project, not a security product — review the code before relying on it, especially before scheduling the silent modes to run unattended.

## Requirements

- Windows (uses `winreg`/WMI; Windows-only)
- Python 3.9+
- Run as Administrator for full functionality (system temp/prefetch cleanup, reliable process termination)

## Installation

```bash
git clone https://github.com/Scorpion691/Optimizer-Pro.git
cd Optimizer-Pro
pip install -r requirements.txt
```

## Usage

```bash
python optimizer_daemon.pyw
```

- **Dashboard** — watch live CPU/RAM stats.
- **USB Shield** — view the live incident log of detected drives and any suspicious files found on them.
- **PURGE NOW** — run an immediate cleanup pass.

### Scheduled / unattended modes

```bash
# One-off silent cleanup, no window (good for a recurring Task Scheduler job)
python optimizer_daemon.pyw --silent-purge

# Cleanup + a short summary dialog (good for a logon trigger)
python optimizer_daemon.pyw --startup-report
```

To run these automatically, create Windows Task Scheduler tasks that launch `pythonw.exe optimizer_daemon.pyw --silent-purge` (e.g. every 12 hours) and/or `--startup-report` (at logon). The script does not register these tasks for you.

## Tech stack

Python · CustomTkinter · psutil · WMI (`wmi` / `pywin32`)

## License

MIT — see [LICENSE](LICENSE).
