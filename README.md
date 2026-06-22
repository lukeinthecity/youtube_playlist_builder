🎵 YouTube Playlist Sync (Utility Edition)



Create playlists from .txt files



Update existing playlists



Avoid duplicates



Remove tracks no longer in file



Prefer official “Topic” uploads



Filter out long videos (>15 min)



Cache results to avoid hitting API quota



📦 Project Structure

youtube\_playlist\_builder/

│

├── main.py

├── client\_secret.json

├── cache.json          (auto-created)

├── solarpunk.txt

├── README.md

└── venv/

🐍 Setup (First Time Only)

1️⃣ Install Python



Download from:

https://www.python.org/downloads/



⚠️ Make sure to check:

“Add Python to PATH”



Verify:



python --version

2️⃣ Create Virtual Environment



Inside your project folder:



python -m venv venv



Activate it:



Windows:



venv\\Scripts\\activate



Mac/Linux:



source venv/bin/activate



You should see:



(venv)

3️⃣ Install Dependencies

pip install google-api-python-client google-auth-oauthlib google-auth-httplib2

4️⃣ Google Cloud Setup



Create project in Google Cloud Console



Enable YouTube Data API v3



Create OAuth Client ID



Application type: Desktop App



Download the JSON file



Rename to:



client\_secret.json



Place it in your project folder.



🎵 Creating a Playlist File



Create a text file like:



solarpunk.txt



Format:



Artist - Track Name

Artist - Track Name

Artist - Track Name



Example:



Vashti Bunyan - Diamond Day

Nick Drake - Northern Sky

Helios - Bless This Morning Year

Tycho - Dive

🚀 Running the Script

Basic Usage

python main.py solarpunk.txt



Playlist name = filename (solarpunk)



Privacy = private



Syncs playlist to match file exactly



Custom Title

python main.py solarpunk.txt --title "Solarpunk Pastoral"

Set Privacy

python main.py solarpunk.txt --privacy public



Options:



private



public



unlisted



Full Example

python main.py solarpunk.txt --title "Solarpunk Pastoral" --privacy unlisted

🔁 Sync Behavior



This script is idempotent.



It will:



Add missing tracks



Skip existing tracks



Remove tracks no longer in file



Use cached matches when possible



Avoid duplicate API searches



Your .txt file is the source of truth.



🧠 Cache System



The script creates:



cache.json



This stores:



video\_id



duration



channel



last\_verified



Benefits:



Massive reduction in API quota usage



Faster reruns



Stable playlist matching



You can delete cache.json anytime to force fresh searches.



⚠️ API Quota Notes



Default YouTube quota: 10,000 units/day



Search requests are expensive (100 units each).



Caching prevents repeated search calls.



If you hit quota:



Wait 24 hours



Or delete fewer tracks



Or rely on cached entries



🛠 Reset Everything



If needed:



Delete:



cache.json



Re-run script to rebuild matches.



🌱 Typical Workflow



Edit playlist text file



Save



Run:



python main.py solarpunk.txt



Done.



🧩 Future Improvements (Optional)



Batch pagination for playlists >50 tracks



Duration matching per track



Logging file



Dry-run mode



Export playlist to Markdown



Cross-platform (Spotify, etc.)



🎯 Philosophy



Text → API → Structured Media



Your playlists are now:



Versionable



Reproducible



Editable in plain text



Fully synced

