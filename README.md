# 🎵 YouTube Playlist Sync (Utility Edition)

A secure, desktop-first automation utility that compiles and syncs YouTube playlists directly from plain-text `.txt` files. By communicating natively with the YouTube Data API v3 from your local environment, this tool completely eliminates the friction of heavy web-app interfaces and browser-bloat.

---

## ✨ Core Mechanics & Features

* **True Idempotent Syncing:** Your text file is the single source of truth. The engine automatically adds missing tracks, skips duplicates, and cleanly prunes remote tracks that have been deleted from the local file.
* **Smart Audio Curation:** * Prioritizes official video configurations by auto-selecting **"- Topic"** channel uploads.
  * Aggressively blocks low-fidelity tracks using an internal word blacklist (`remix`, `cover`, `slowed`, `sped up`, `reaction`, etc.).
* **Dynamic Audio Filters:**
  * **User-Defined Durations:** Set precise maximum video lengths to smoothly include everything from quick 2-minute tracks to massive 30+ minute ambient soundscapes and progressive epics.
  * **Conditional Live Inclusions:** Toggle the inclusion of live performances on the fly, bypassing the standard keyword filters when you want to capture concerts or session recordings.
* **Quota Preservation Engine:** Video lookups are mapped and preserved inside a local cache file. This massively slashes expensive search quota usage (100 units per search) and makes subsequent sync executions instantaneous.
* **Dual Execution Modes:** Fully operational via a streamlined terminal interface or a native cross-platform desktop UI window.

---

## 📦 Project Structure

```text
youtube-playlist-builder/
│
├── main.py             # Core API Engine, Filter Validation & CLI Entrypoint
├── gui.py              # Tkinter-based Desktop UI with Custom Filter Controls
├── .gitignore          # Firewall configuration excluding local keys & caches
├── README.md           # Documentation
│
├── solarpunk.txt       # Example plain-text playlist target
│
├── client_secret.json  # USER PROVIDED: Google Cloud Console OAuth Key
├── token.json          # AUTOMATIC: Secured OAuth Session Persistence Token
└── cache.json          # AUTOMATIC: Persistent Track-to-Video API Mapping Cache
