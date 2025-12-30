import os
import random
import requests
import yt_dlp
from dotenv import load_dotenv

# Load API keys
load_dotenv()

class AssetManager:
    def __init__(self):
        # API Keys
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.pixabay_api_key = os.getenv("PIXABAY_API_KEY")
        
        # Endpoints
        self.pexels_video_url = "https://api.pexels.com/videos/search"
        self.pexels_image_url = "https://api.pexels.com/v1/search"
        self.pixabay_image_url = "https://pixabay.com/api/"
        self.pixabay_video_url = "https://pixabay.com/api/videos/"
        
        # Paths
        self.music_folder = os.path.join("assets", "background_music")
        self.temp_folder = os.path.join("assets", "temp")
        
        os.makedirs(self.temp_folder, exist_ok=True)
        os.makedirs(self.music_folder, exist_ok=True)

    def get_music(self, query="motivational"):
        """
        1. Checks if a file SPECIFICALLY matching the 'query' already exists.
        2. If not, uses yt-dlp to download it.
        """
        print(f"🔍 Looking for music matching: '{query}'...")
        
        # 1. Clean the query to match filenames (e.g., "Slow Reverb" -> "slow_reverb")
        sanitized_query = query.lower().replace(" ", "_")
        
        # 2. Get all MP3s
        existing_files = [f for f in os.listdir(self.music_folder) if f.endswith(".mp3")]
        
        # 3. Check for a SPECIFIC match
        # We look for files that contain our sanitized query in their name
        matching_files = [f for f in existing_files if sanitized_query in f.lower()]

        if matching_files:
            selected = matching_files[0] # Pick the first match found
            print(f"✅ Found cached music: {selected}")
            return os.path.join(self.music_folder, selected)

        # 4. If NO match found, Force Download
        print(f"⬇️ No local match for '{query}'. Downloading from YouTube...")
        return self._download_music_from_youtube(query)

    def _download_music_from_youtube(self, search_query):
        """
        Uses yt-dlp to search and download audio, strictly limited to < 60 seconds.
        """
        # --- FIX: Add the query to the filename so we can find it next time! ---
        clean_query = search_query.replace(" ", "_")
        # Example output: assets/background_music/gym_phonk_Epic_Song_Title.mp3
        output_template = os.path.join(self.music_folder, f"{clean_query}_%(title)s.%(ext)s")
        
        # Filter function to skip videos longer than 10 mins (600s)
        def longer_than_10_mins(info, *, incomplete):
            duration = info.get('duration')
            if duration and duration > 600: 
                return 'Video too long (>10 mins), skipping...'

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_template,
            'match_filter': longer_than_10_mins, # 1. Skip long mixes
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'postprocessor_args': [
                '-t', '60' # 2. FORCE TRIM: Keep only first 60 seconds
            ],
            'noplaylist': True,
            'quiet': True,
            'default_search': 'ytsearch5', # Search 5 videos (in case first is too long)
            'restrictfilenames': True # Ensure filenames are clean (ASCII only)
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                print(f"🔍 Searching & Downloading (Max 60s): '{search_query}'...")
                # We specifically search for "Audio" to avoid official music videos with long intros sometimes
                ydl.download([search_query]) # Direct download call
                
                print("✅ Download & Trim Complete.")
                
            # Re-scan folder to find the new file
            # We look for the file we just likely created (contains our query)
            files = [f for f in os.listdir(self.music_folder) if f.endswith(".mp3")]
            
            # Find the newest file that matches our query
            matching_new_files = [f for f in files if clean_query in f]
            
            if matching_new_files:
                # Get the most recently created one
                newest_file = max([os.path.join(self.music_folder, f) for f in matching_new_files], key=os.path.getctime)
                print(f"🎵 New Music Ready: {os.path.basename(newest_file)}")
                return newest_file
            else:
                # Fallback: Just get the newest file period (if query matching failed in filename)
                newest_file = max([os.path.join(self.music_folder, f) for f in files], key=os.path.getctime)
                return newest_file

        except Exception as e:
            print(f"❌ Music Download Failed: {e}")
            return None

    # --- VISUAL ASSETS (Unchanged) ---
    def get_background_video(self, query="nature", duration_min=10):
        try:
            print(f"1️⃣ [Pexels] Searching for video: '{query}'...")
            return self._fetch_pexels_asset(query, asset_type="video", min_duration=duration_min)
        except Exception:
            if self.pixabay_api_key:
                print(f"2️⃣ [Pixabay] Searching for video (Backup): '{query}'...")
                return self._fetch_pixabay_asset(query, asset_type="video", min_duration=duration_min)
            raise Exception("❌ Visual assets search failed.")

    def get_background_image(self, query="nature"):
        try:
            print(f"1️⃣ [Pexels] Searching for image: '{query}'...")
            return self._fetch_pexels_asset(query, asset_type="image")
        except Exception:
            if self.pixabay_api_key:
                print(f"2️⃣ [Pixabay] Searching for image (Backup): '{query}'...")
                return self._fetch_pixabay_asset(query, asset_type="image")
            raise Exception("❌ Visual assets search failed.")

    # --- INTERNAL HELPERS (Unchanged) ---
    def _fetch_pexels_asset(self, query, asset_type, min_duration=0):
        if not self.pexels_api_key: raise ValueError("PEXELS_API_KEY missing")
        headers = {"Authorization": self.pexels_api_key}
        
        if asset_type == "video":
            url = self.pexels_video_url
            params = {"query": query, "per_page": 10, "orientation": "portrait", "size": "medium"}
        else:
            url = self.pexels_image_url
            params = {"query": query, "per_page": 10, "orientation": "portrait", "size": "large"}

        r = requests.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()
        items = data.get("videos") if asset_type == "video" else data.get("photos")
        
        if not items: raise FileNotFoundError(f"No {asset_type} found on Pexels.")
        
        if asset_type == "video":
            valid = [v for v in items if v['duration'] >= min_duration] or items
            sel = random.choice(valid)
            link = sorted(sel['video_files'], key=lambda x: x['width'], reverse=True)[0]['link']
            ext = "mp4"
            iid = sel['id']
        else:
            sel = random.choice(items)
            link = sel['src']['large2x']
            ext = "jpg"
            iid = sel['id']
            
        return self._download_asset(link, f"pexels_{query}_{iid}.{ext}")

    def _fetch_pixabay_asset(self, query, asset_type="video", min_duration=0):
        if not self.pixabay_api_key: raise ValueError("PIXABAY_API_KEY missing")
        url = self.pixabay_video_url if asset_type == "video" else self.pixabay_image_url
        params = {"key": self.pixabay_api_key, "q": query, "per_page": 10, "orientation": "vertical", "video_type": "all", "image_type": "photo"}
        
        r = requests.get(url, params=params)
        r.raise_for_status()
        items = r.json().get("hits")
        if not items: raise FileNotFoundError(f"No {asset_type} found on Pixabay.")
        
        sel = random.choice(items)
        if asset_type == "video":
            vids = sel.get('videos', {})
            link = vids.get('medium', {}).get('url') or vids.get('small', {}).get('url')
            ext = "mp4"
        else:
            link = sel.get('largeImageURL')
            ext = "jpg"
            
        return self._download_asset(link, f"pixabay_{query}_{sel['id']}.{ext}")

    def _download_asset(self, url, filename):
        path = os.path.join(self.temp_folder, filename)
        if os.path.exists(path) and os.path.getsize(path) > 0: return path
        print(f"⬇️ Downloading: {filename}...")
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192): f.write(chunk)
        return path

# --- TEST BLOCK ---
if __name__ == "__main__":
    manager = AssetManager()
    print("\n--- ASSET MANAGER V5 TEST (Specific Music Search) ---")
    
    # Test 1: Search for something new
    print("\n🎵 Test 1: Downloading NEW music (Query: 'cyberpunk')...")
    music_path = manager.get_music("cyberpunk")
    print(f"   Result: {music_path}")

    # Test 2: Search for the SAME thing (Should be instant/cached)
    print("\n🎵 Test 2: Searching for SAME music (Query: 'cyberpunk')...")
    music_path_2 = manager.get_music("cyberpunk")
    print(f"   Result: {music_path_2}")