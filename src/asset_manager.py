import os
import random
import requests
from dotenv import load_dotenv

# Load API keys from .env file
load_dotenv()

class AssetManager:
    def __init__(self):
        self.pexels_api_key = os.getenv("PEXELS_API_KEY")
        self.base_url = "https://api.pexels.com/videos/search"
        self.music_folder = "assets/background_music"
        self.temp_folder = "assets/temp"
        
        # Ensure temp folder exists
        os.makedirs(self.temp_folder, exist_ok=True)

    def get_background_video(self, query="nature", duration_min=10):
        """
        Searches Pexels for a vertical video matching the query.
        Downloads it and returns the file path.
        """
        if not self.pexels_api_key:
            raise ValueError("❌ Error: PEXELS_API_KEY not found in .env file.")

        headers = {
            "Authorization": self.pexels_api_key
        }
        
        # We request 'portrait' orientation for Shorts/Reels
        params = {
            "query": query,
            "per_page": 15,
            "orientation": "portrait", 
            "size": "medium" # 'medium' is fast and good enough for mobile
        }

        print(f"🔍 Searching Pexels for: '{query}'...")
        response = requests.get(self.base_url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise ConnectionError(f"Pexels API Error: {response.status_code}")

        data = response.json()
        videos = data.get("videos", [])

        if not videos:
            raise FileNotFoundError(f"No videos found for query: {query}")

        # Pick a random video from the results
        # We try to find one that isn't too short (< 5 seconds is bad)
        valid_videos = [v for v in videos if v['duration'] >= duration_min]
        
        if not valid_videos:
            print("⚠️ No long videos found, picking random one...")
            selected_video = random.choice(videos)
        else:
            selected_video = random.choice(valid_videos)

        # Get the download link (highest quality available in the object)
        video_files = selected_video['video_files']
        # Sort by quality (width) to get a decent one, but not 4k (too heavy)
        video_files.sort(key=lambda x: x['width'], reverse=True)
        download_url = video_files[0]['link']

        # Define output path
        video_filename = f"bg_{query}_{selected_video['id']}.mp4"
        output_path = os.path.join(self.temp_folder, video_filename)

        # Download if we don't have it yet
        if not os.path.exists(output_path):
            print(f"⬇️ Downloading background video...")
            self._download_file(download_url, output_path)
        else:
            print(f"✅ Video already exists locally.")

        return output_path

    def get_random_music(self):
        """
        Selects a random MP3 from the assets/background_music folder.
        """
        files = [f for f in os.listdir(self.music_folder) if f.endswith(".mp3")]
        
        if not files:
            print("⚠️ Warning: No music found in assets/background_music.")
            return None # Handle None in the main engine
        
        selected_music = random.choice(files)
        print(f"🎵 Selected Music: {selected_music}")
        return os.path.join(self.music_folder, selected_music)

    def _download_file(self, url, path):
        """Helper to download file in chunks"""
        with requests.get(url, stream=True) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print("✅ Download complete.")

# --- Testing Block (Run this file directly to test) ---
if __name__ == "__main__":
    manager = AssetManager()
    
    try:
        # Test 1: Fetch a video
        video_path = manager.get_background_video("ocean")
        print(f"Test Video Path: {video_path}")
        
        # Test 2: Fetch music (Make sure you put 1 MP3 in the folder first!)
        music_path = manager.get_random_music()
        print(f"Test Music Path: {music_path}")
        
    except Exception as e:
        print(f"❌ Test Failed: {e}")