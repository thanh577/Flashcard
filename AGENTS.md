# FlashcardApp — AGENTS.md

Python/PyQt6 desktop flashcard app (English/Chinese/Linux CLI). Vietnamese UI.

## Quick start

```bash
python app.py
```

No `requirements.txt` or `pyproject.toml`. Dependencies (install manually):
- `PyQt6` (core GUI)
- `pyinstaller` (packaging only, not needed to run)
- TTS fallback chain: `edge-tts` → `gtts-cli` → `espeak-ng` → `espeak` (any works)

A `venv/` directory is present at project root.

## No tests, no linter, no formatter

Zero test files, no test framework, no `ruff`, `black`, or formatter config. Skip any verification step that assumes these exist.

## Build & package

- **Windows .exe**: `pyinstaller FlashcardApp.spec` (must run on a real Windows machine; no cross-compile)
- **Linux AppImage**: `bash build_appimage.sh` (runs natively on Linux)
- **CI (both)**: `.github/workflows/build-windows.yml` — triggered on push, runs on GitHub-hosted Windows + Ubuntu runners

Never use `pyinstaller --onefile app.py` directly — the `.spec` file bundles seed JSON data and icon.

## Architecture

```
app.py              ← entrypoint (QApplication + MainWindow)
core/
  paths.py          ← resource_path() (frozen/readonly) vs user_data_dir() (writeable)
  storage.py        ← SQLite DB + config.json management
  scheduler.py      ← SM-2 spaced repetition algorithm
  audio.py          ← TTS via edge-tts/gtts-cli/espeak-ng/espeak
  ai_lookup.py      ← Groq API (llama-3.3-70b-versatile) for Linux command explain
  theme.py          ← QSS + colour constants
  stats.py          ← streak & badge calculations
ui/                 ← all PyQt6 widgets (main_window, flashcard, dialogs)
data/               ← seed JSON files (english.json, chinese.json, linux.json) + dev-mode DB/config
```

## Data flow

- **Seed data** (read-only): `data/*.json` bundled into exe at build time via `FlashcardApp.spec`. Used only on first-ever run.
- **Live data** (read-write): `flashcard.db` + `config.json` live in `user_data_dir()`:
  - dev mode → `data/` in project root
  - frozen Windows → `%APPDATA%\FlashcardApp\`
  - frozen Linux → `~/.local/share/FlashcardApp/`
- Reset progress: delete the user data directory above.

## Key quirks

- All UI text is in **Vietnamese**.
- Keyboard shortcuts: `Ctrl+Alt+N` (next card), `Ctrl+Alt+S` (speak), `Space` (flip card)
- Audio requires a system TTS CLI tool; no Python TTS library is bundled.
- AI lookup requires a Groq API key (entered in Settings).
- App minimises to system tray on close (does not quit) — use tray menu "❌ Thoát" to actually exit.
- Desktop widget runs alongside main window; can be toggled from tray.
- SM-2 scheduler maps quality: `again→0`, `hard→3`, `good→4`, `easy→5`.
- DB backups kept at `./backups/flashcard_YYYYMMDD_HHMMSS.db` (max 5).
- Log file: `app.log` in `user_data_dir()`.
