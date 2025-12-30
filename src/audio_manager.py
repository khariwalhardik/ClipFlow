import os
import asyncio
import edge_tts
import whisper

class AudioManager:
    def __init__(self):
        # Voice Options: 
        # "en-US-ChristopherNeural" (Deep Male)
        # "en-US-AriaNeural" (Clear Female)
        self.voice = "en-US-ChristopherNeural"
        
        # Load the Whisper model locally (runs on your CPU/GPU)
        # 'base' is a good balance of speed and accuracy.
        print("🎧 Loading Whisper Model... (this happens once)")
        self.transcriber = whisper.load_model("base")

    async def generate_voiceover(self, text: str, output_path: str) -> str:
        """
        Converts text input into an MP3 audio file using Edge TTS.
        """
        print(f"🗣️ Generating voiceover for: '{text[:20]}...'")
        communicate = edge_tts.Communicate(text, self.voice)
        await communicate.save(output_path)
        
        if os.path.exists(output_path):
            return output_path
        else:
            raise FileNotFoundError("❌ Failed to generate voiceover file.")

    def transcribe_audio(self, audio_path: str):
        """
        Extracts text from audio with precise timestamps.
        Required for creating subtitles.
        """
        print(f"📝 Transcribing audio: {os.path.basename(audio_path)}...")
        
        # This runs the neural network locally
        result = self.transcriber.transcribe(audio_path)
        
        # Result contains: {'text': ..., 'segments': [{'start': 0.0, 'end': 2.0, 'text': 'Hi'}, ...]}
        return result

# --- Testing Block ---
if __name__ == "__main__":
    # Simple test to ensure libraries are working
    manager = AudioManager()
    
    # Needs an async loop to run
    loop = asyncio.get_event_loop_policy().get_event_loop()
    loop.run_until_complete(manager.generate_voiceover("Hello world", "test.mp3"))
    print("✅ Audio Manager Test Passed")