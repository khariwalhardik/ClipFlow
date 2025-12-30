import os

def create_structure():
    # Define the root directory
    root_dir = "/home/hkhariwal/Desktop/Projects/motivAgent"

    # Define the folder structure
    folders = [
        f"{root_dir}/assets/background_music",
        f"{root_dir}/assets/fonts",
        f"{root_dir}/assets/temp",
        f"{root_dir}/output",
        f"{root_dir}/src",
    ]

    # Define the files to create
    files = [
        f"{root_dir}/src/__init__.py",
        f"{root_dir}/src/audio_manager.py",
        f"{root_dir}/src/asset_manager.py",
        f"{root_dir}/src/video_engine.py",
        f"{root_dir}/src/uploader.py",
        f"{root_dir}/.env",
        f"{root_dir}/main.py",
        f"{root_dir}/requirements.txt"
    ]

    # Create Folders
    print("🚀 Starting Project Setup...")
    for folder in folders:
        try:
            os.makedirs(folder, exist_ok=True)
            print(f"✅ Created folder: {folder}")
        except OSError as e:
            print(f"❌ Error creating {folder}: {e}")

    # Create Files
    for file_path in files:
        try:
            with open(file_path, 'w') as f:
                pass # Create empty file
            print(f"📄 Created file: {file_path}")
        except IOError as e:
            print(f"❌ Error creating {file_path}: {e}")

    # Create a README instruction
    with open(f"{root_dir}/readme.txt", "w") as f:
        f.write("Project Structure Created Successfully.\n")
        f.write("1. Add your 10 MP3 music files to assets/background_music/\n")
        f.write("2. Add a .ttf font file to assets/fonts/\n")
        f.write("3. Fill in the .env file with your API keys.\n")
    
    print("\n✨ Project Structure Built Successfully! ✨")
    print(f"📂 Go to the '{root_dir}' folder to start.")

if __name__ == "__main__":
    create_structure()