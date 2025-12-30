import os
import asyncio
import time
from src.audio_manager import AudioManager
from src.asset_manager import AssetManager
from src.video_engine import VideoEngine
from src.uploader import Uploader

async def main():
    print("\n========================================")
    print("🤖 CLIPFLOW: AI CONTENT FACTORY")
    print("========================================\n")

    # 1. INITIALIZE MODULES
    try:
        print("🔌 Initializing Engines...")
        audio_mgr = AudioManager()
        asset_mgr = AssetManager()
        video_eng = VideoEngine()
        uploader = Uploader()
        print("✅ Systems Online.\n")
    except Exception as e:
        print(f"❌ Init Error: {e}")
        return

    os.makedirs("output", exist_ok=True)
    os.makedirs("assets/temp", exist_ok=True)

    # 2. SELECT CREATION MODE
    print("Select Mode:")
    print("1. 🧠 Quote Video (Solid Black + White Text + Music)")
    print("2. 🗣️ AI Story Short (Text-to-Speech + Stock Video)")
    print("3. 🎤 Personal Short (Record Voice + Stock Video)")
    choice = input("👉 Enter choice (1-3): ").strip()

    # Setup variables
    base_filename = f"project_{int(time.time())}"
    audio_path = None
    transcription = ""
    background_path = None
    music_path = None
    
    # --- LOGIC BRANCHES ---

    # === MODE 1: QUOTE VIDEO (Text Only) ===
    if choice == "1":
        print("\n--- 🧠 QUOTE MODE ---")
        quote = input("📝 Paste your quote/text: ")
        transcription = quote # Raw text for video engine
        
        # Force specific settings for this style
        audio_path = None  # No voice
        background_path = "solid_black" # Triggers the pro black background
        
        music_vibe = input("🎵 Music Vibe (e.g., dark, ambient, epic): ") or "dark ambient"
        music_path = asset_mgr.get_music(music_vibe)

    # === MODE 2: AI STORY (TTS + Visuals) ===
    elif choice == "2":
        print("\n--- 🗣️ AI STORY MODE ---")
        script = input("📝 Enter your script: ")
        
        # 1. Generate Audio
        print("\nSelect Voice:")
        print("  (m) Male  (f) Female  (im) Indian Male  (bm) British Male")
        v_choice = input("  > ").strip().lower()
        voice_map = {"m": "male", "f": "female", "im": "ind_male", "bm": "british_male"}
        
        audio_path = f"assets/temp/{base_filename}.mp3"
        await audio_mgr.generate_voiceover(script, audio_path, voice_type=voice_map.get(v_choice, "male"))
        
        # 2. Get Visuals
        visual_query = input("🎨 Background Vibe (e.g., money, gym, nature): ")
        background_path = asset_mgr.get_background_video(visual_query)
        
        # 3. Get Music
        music_vibe = input("🎵 Music Vibe (e.g., phonk, lo-fi): ") or "motivational"
        music_path = asset_mgr.get_music(music_vibe)
        
        # 4. Transcribe (for accurate timing)
        print("📜 Generating Subtitles...")
        transcription = audio_mgr.transcribe_audio(audio_path)

    # === MODE 3: PERSONAL SHORT (Mic + Visuals) ===
    elif choice == "3":
        print("\n--- 🎤 PERSONAL MODE ---")
        duration = input("⏱️ Recording Duration (seconds): ")
        duration = int(duration) if duration.isdigit() else 10
        
        audio_path = f"assets/temp/{base_filename}.wav"
        input(f"🔴 Press ENTER to record for {duration}s...")
        audio_mgr.record_audio_from_mic(audio_path, duration_sec=duration)
        
        # 2. Get Visuals
        visual_query = input("🎨 Background Vibe (e.g., working, coding, city): ")
        background_path = asset_mgr.get_background_video(visual_query)
        
        # 3. Get Music
        music_vibe = input("🎵 Music Vibe (e.g., jazz, hiphop): ") or "chill"
        music_path = asset_mgr.get_music(music_vibe)
        
        # 4. Transcribe
        print("📜 Generating Subtitles...")
        transcription = audio_mgr.transcribe_audio(audio_path)

    else:
        print("❌ Invalid choice.")
        return

    # --- STEP 4: VIDEO ASSEMBLY ---
    print(f"\n🎬 ASSEMBLING VIDEO...")
    final_output = f"output/final_{base_filename}.mp4"
    
    try:
        video_eng.create_video(
            audio_path=audio_path,
            background_path=background_path,
            music_path=music_path,
            output_path=final_output,
            transcription=transcription
        )
    except Exception as e:
        print(f"❌ Video Engine Failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # --- STEP 5: UPLOAD ---
    print("\n🚀 UPLOAD STATION")
    upload_yn = input("Upload to YouTube Shorts? (y/n): ").lower()
    
    if upload_yn == 'y':
        title = input("Enter Title: ")
        desc = input("Enter Description: ") or f"#shorts #motivation #{music_vibe if music_path else 'ai'}"
        
        success = uploader.upload_to_youtube(final_output, title, desc)
        if success:
            print("🎉 Mission Accomplished.")
        else:
            print("⚠️ Upload failed, but video is saved locally.")
    else:
        print(f"✅ Video saved locally at: {final_output}")

if __name__ == "__main__":
    asyncio.run(main())