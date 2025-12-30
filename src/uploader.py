import os
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

class Uploader:
    def __init__(self):
        # YouTube Setup
        self.scopes = ["https://www.googleapis.com/auth/youtube.upload"]
        self.client_secrets_file = "client_secrets.json"
        self.token_file = "token.json"  # <--- NEW: File to store your login
        
        # Instagram Setup
        self.instagram_access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN")
        self.instagram_account_id = os.getenv("INSTAGRAM_ACCOUNT_ID")

    def upload_to_youtube(self, video_path, title, description):
        print(f"\n🚀 STARTING YOUTUBE UPLOAD: {title}")
        
        if not os.path.exists(self.client_secrets_file):
            print("❌ Error: 'client_secrets.json' not found.")
            return False

        # --- 1. AUTHENTICATION (AUTO-LOGIN LOGIC) ---
        creds = None
        
        # Check if we already have a valid login saved
        if os.path.exists(self.token_file):
            print("🔑 Found saved credentials (token.json). Logging in silently...")
            creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

        # If no valid credentials, let's log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                print("🔄 Token expired. Refreshing...")
                creds.refresh(Request())
            else:
                print("🌐 First time login: Opening browser...")
                flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                    self.client_secrets_file, self.scopes)
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for next time
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
                print("✅ Login saved to 'token.json' for future use.")

        # Build the YouTube Service
        youtube = googleapiclient.discovery.build("youtube", "v3", credentials=creds)

        # --- 2. UPLOAD CONFIG ---
        body = {
            "snippet": {
                "title": title[:100], 
                "description": description,
                "tags": ["AI", "Shorts", "Motivation"],
                "categoryId": "22" # People & Blogs
            },
            "status": {
                "privacyStatus": "private", # Change to "public" when ready
                "selfDeclaredMadeForKids": False
            }
        }

        # --- 3. EXECUTE UPLOAD ---
        try:
            print(f"📤 Uploading file: {video_path}")
            media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
            request = youtube.videos().insert(
                part="snippet,status",
                body=body,
                media_body=media
            )
            
            response = None
            while response is None:
                status, response = request.next_chunk()
                if status:
                    print(f"   > Progress: {int(status.progress() * 100)}%")

            print(f"✅ UPLOAD SUCCESS! Video ID: {response['id']}")
            print(f"🔗 Link: https://youtu.be/{response['id']}")
            return True

        except Exception as e:
            print(f"❌ YouTube Upload Failed: {e}")
            return False

    def upload_to_instagram(self, video_path, caption):
        print("⚠️ Instagram requires hosting. Skipping for now.")
        pass

# --- TEST BLOCK ---
if __name__ == "__main__":
    if not os.path.exists("test_video.mp4"):
        print("❌ Please put a 'test_video.mp4' in this folder to test.")
        exit()

    uploader = Uploader()
    # Test Title with timestamp to allow multiple uploads of same file
    import time
    uploader.upload_to_youtube("test_video.mp4", f"Auto Upload Test {int(time.time())}", "#shorts")