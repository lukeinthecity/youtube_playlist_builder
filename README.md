# 🎵 YouTube Playlist Builder desktop utility

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
* **Dual Execution Modes:** Fully operational via a native cross-platform desktop UI window or a streamlined terminal interface.

---

## 📦 Project Structure

```text
youtube-playlist-builder/
│
├── main.py             # Core API Engine, Filter Validation & CLI Entrypoint
├── gui.py              # Tkinter-based Desktop UI with Custom Filter Controls
├── .gitignore          # Firewall configuration excluding local keys & caches
├── LICENSE             # MIT Open-Source License Terms
├── README.md           # Documentation
│
├── client_secret.json  # USER PROVIDED: Google Cloud Console OAuth Key
├── token.json          # AUTOMATIC: Secured OAuth Session Persistence Token
└── cache.json          # AUTOMATIC: Persistent Track-to-Video API Mapping Cache
```

---

## 🐍 Setup & Environment Initialization

### 1. Initialize Virtual Environment
Navigate to your project directory inside your terminal and establish an isolated virtual environment:

```bash
# Create the environment
python -m venv venv

# Activate on Windows (Command Prompt):
venv\Scripts\activate

# Activate on Mac / Linux:
source venv/bin/activate
```

### 2. Install Dependencies
Install the required Google API integration components and optional UI enhancements:

```bash
pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

# Optional: Enables seamless drag-and-drop integration in the GUI layout
pip install tkinterdnd2
```

---

## 🔐 Google Cloud Configuration Gate (Linking the API to the GUI)

Because this utility is entirely open-source, you must supply your own secure credentials from the Google Cloud Console. Follow these steps to generate your keys:

1. **Create Project:** Go to [Google Cloud Console](https://console.cloud.google.com/) and create a new project**.
2. **Configure Consent:** Navigate to **APIs & Services > OAuth consent screen**.  Create an **External** app, add your email to **Test users**, and save**.
4. **Generate Keys:** Go to **Credentials > + Create Credentials > OAuth client ID**. Select **Desktop app**, create, and **Download JSON**.
5.  **Configure YouTube API** Click on **API Library**. Search for and enable the **YouTube Data API v3**.
6. **Link to App:** Move the downloaded file into your root folder and rename it exactly to `client_secret.json`.

---

## 🚀 Execution Guide

### Method A: Graphical Desktop Interface (Recommended)
For a seamless, interactive configuration flow, launch the multi-threaded desktop GUI dashboard:

```bash
python gui.py
```

* **Automatic Credentials Handshake:** The application automatically detects `client_secret.json` on launch.
* **Custom Filtering Controllers:** Adjust the duration spinbox to shift maximum acceptable video length restrictions from 1 to 180 minutes, or toggle the "Allow Live Tracks" checkbox to dictate inclusion settings instantly.
* **Drag-and-Drop Staging:** Drag any playlist `.txt` file from your computer and drop it directly onto the entry field to instantly queue it up for processing.
* **System-Aware Themes:** Automatically transitions between Dark Mode and Light Mode layouts based on your OS settings.

### Method B: CLI Sync Engine (For Technical Users)
The command-line interface treats your local `.txt` filename as the playlist name and updates it on the fly. Create a text file with tracks ordered line-by-line (e.g., `my_list.txt`):

```text
Artist - Track Name
Artist - Track Name
```

Run the sync using standard execution flags:

```bash
# Basic Private Sync (Default 15-minute cap, Live filtered out)
python main.py my_list.txt

# Sync with custom constraints
python main.py my_list.txt --max-duration 45 --allow-live --privacy unlisted
```

---

## 🛡️ Security & State Persistence

This tool separates core public logic from local runtime files. 

* **`token.json`:** Generated automatically upon your first secure login. It handles re-authentication in the background via secure OAuth2 refresh keys.
* **`cache.json`:** Safely tracks query maps. If you adjust your duration configurations, the engine will smartly look past cached entries that violate your new limits and perform fresh searches.

---

## 🛠️ Troubleshooting & Configuration Gotchas

Because this tool runs in a local sandbox mode utilizing personal Google Cloud Console keys, you might encounter a few edge-case behaviors during your first synchronization handshake. Here is how to navigate them:

### 1. 🛑 Error 403: access_denied / "Access Blocked: App Not Verified"
* **The Symptom:** When trying to log into your Google account via the browser window, Google blocks the flow and displays a security warning or an access error.
* **The Cause:** Your Google Cloud project is in **Testing** mode (which is completely fine and normal). However, Google will aggressively block any authentication attempt unless the specific login email has been manually white-listed.
* **The Fix:**
  1. Open the [Google Cloud Console](https://console.cloud.google.com/).
  2. Navigate to **APIs & Services** > **OAuth consent screen**.
  3. Scroll down to the **Test users** sub-section and click **+ ADD USERS**.
  4. Type your exact Google/YouTube email address, click **Add**, and save.
  5. Close the hung browser window, restart the utility, and log in again.

### 2. 🔍 Missing "Test Users" Section in Google Cloud
* **The Symptom:** You are looking at the OAuth consent configuration screen, but the entire "Test Users" portal is missing from the interface.
* **The Cause:** You selected **Internal** instead of **External** for the User Type. Internal setups are locked strictly to corporate Google Workspace domains. Standard `@gmail.com` accounts will be frozen out.
* **The Fix:**
  1. On the **OAuth consent screen** dashboard, click the **Make External** button (or click *Edit App*).
  2. Reconfigure the User Type to **External**.
  3. Advance to the **Test users** setup step, add your email address, and hit save.

### 3. 👻 Error 404: "The playlist identified with the request's playlistId cannot be found"
* **The Symptom:** The script crashes out or dumps an `HttpError 404` directly into the activity log targeting a specific playlist ID string.
* **The Cause:** This is caused by **YouTube API replication lag** or a stale **Ghost Playlist**. If you recently deleted an old playlist on YouTube that matches the name of your text file, Google's distributed database nodes might still temporarily return the dead ID. When the engine attempts to add tracks to it, the server realizes it doesn't exist and throws a 404.
* **The Fix:**
  * **Option A:** Simply rename your local `.txt` file to something fresh (e.g., from `music.txt` to `my_tracks.txt`) to force the engine to bypass the stale server cache and create a clean setup.
  * **Option B:** Close the GUI, delete the auto-generated `cache.json` from your root workspace folder to clear your local lookup maps, and re-run `python gui.py`.

### ⚠️ A Note on the "Unsafe App" Warning
When authenticating in your web browser for the first time, Google will display a screen stating *"Google hasn't verified this app."* This is completely standard behavior for open-source development files. 

To bypass it safely:
1. Click the small **Advanced** link at the bottom of the warning text block.
2. Click **Go to Playlist Builder (unsafe)**.
3. Grant the script permission to manage your playlists. Your authentication credentials will be locked safely inside your local directory as `token.json` and will never be shared.
