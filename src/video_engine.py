import os
import glob
import PIL.Image

# --- MONKEY PATCH FOR PILLOW 10.0.0+ ---
if not hasattr(PIL.Image, 'ANTIALIAS'):
    PIL.Image.ANTIALIAS = PIL.Image.LANCZOS

from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, ImageClip, ColorClip,
    CompositeVideoClip, CompositeAudioClip
)
from moviepy.video.fx.all import crop, fadein, fadeout

# Import AudioManager for the test block only
if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd()) 
    from src.audio_manager import AudioManager

class VideoEngine:
    def __init__(self):
        # --- 🎨 CONFIGURATION (Professional White Quote Style) ---
        self.style = {
            # 'Impact' is a great, bold choice for this style. 'Arial-Bold' is a safe fallback.
            "font": "Impact" if os.name == 'nt' else "DejaVuSans-Bold", 
            "fontsize": 60,               # Very Large, imposing font
            "color": 'white',             # Clean white
            "stroke_color": 'black',      # No outline needed against black
            "stroke_width": 0,
            "position": ('center', 'center'),
            "fade_duration": 2.0
        }

    def create_video(self, audio_path, background_path, music_path, output_path, transcription):
        print(f"🎬 Starting Assembly...")
        
        # 1. Determine Duration & Voice
        voice_clip = None
        video_duration = 10.0 # Default duration
        
        if audio_path and os.path.exists(audio_path):
            try:
                voice_clip = AudioFileClip(audio_path).volumex(0.4)
                video_duration = voice_clip.duration
                print(f"   > Mode: Voiceover Detected. Duration: {video_duration:.2f}s")
            except Exception as e:
                print(f"⚠️ Failed to load voice: {e}. Switching to 10s Text-Only mode.")
                voice_clip = None
        else:
            print(f"   > Mode: No Voice detected. Setting fixed duration: {video_duration}s")

        # 2. Load Background (Priority: Solid Black -> Image -> Video)
        # We prioritize solid black here to match the requested style, but keep image/video logic for flexibility.
        if not background_path or not os.path.exists(background_path) or "solid_black" in str(background_path):
             print("⬛ Creating solid black background (requested style).")
             video_clip = ColorClip(size=(1080, 1920), color=(0, 0, 0)).set_duration(video_duration)
             video_clip.fps = 24
        elif background_path.lower().endswith(('.jpg', '.jpeg', '.png')):
            print(f"🖼️ Detected IMAGE background: {os.path.basename(background_path)}")
            video_clip = ImageClip(background_path).set_duration(video_duration)
            video_clip.fps = 24
        else:
            print(f"🎥 Detected VIDEO background: {os.path.basename(background_path)}")
            video_clip = VideoFileClip(background_path)
            if video_clip.duration < video_duration:
                video_clip = video_clip.loop(duration=video_duration)
            else:
                video_clip = video_clip.subclip(0, video_duration)

        # 3. Crop & Resize
        w, h = video_clip.size
        target_ratio = 9/16
        new_w = h * target_ratio
        if w > new_w:
            x_center = w / 2
            video_clip = crop(video_clip, width=new_w, height=h, x_center=x_center, y_center=h/2)
        video_clip = video_clip.resize(height=1920)

        # 4. Audio Mixing
        print(f"🎵 Checking Music Path: {music_path}")
        final_audio = None
        if music_path and os.path.exists(music_path):
            try:
                music_clip = AudioFileClip(music_path)
                if music_clip.duration < video_duration:
                    music_clip = music_clip.loop(duration=video_duration)
                else:
                    music_clip = music_clip.subclip(0, video_duration)
                
                if voice_clip:
                    music_clip = music_clip.volumex(0.40)
                    final_audio = CompositeAudioClip([voice_clip, music_clip])
                else:
                    music_clip = music_clip.volumex(1.0)
                    final_audio = music_clip
                print("   > Audio Mixed Successfully.")
            except Exception as e:
                print(f"❌ ERROR LOADING MUSIC: {e}")
                final_audio = voice_clip
        else:
            final_audio = voice_clip

        if final_audio:
            video_clip = video_clip.set_audio(final_audio)

        # 5. Generate Text with Quotation Marks
        segments = []
        raw_text = ""
        if isinstance(transcription, dict) and 'segments' in transcription:
            segments = transcription['segments']
        elif isinstance(transcription, str):
            raw_text = transcription
            segments = [{'start': 0, 'end': video_duration, 'text': raw_text}]
        elif isinstance(transcription, dict) and 'text' in transcription:
            raw_text = transcription['text']
            segments = [{'start': 0, 'end': video_duration, 'text': raw_text}]

        # --- NEW: Automatically add quotes to single-block text ---
        if len(segments) == 1 and not segments[0]['text'].strip().startswith('"'):
             segments[0]['text'] = f'“{segments[0]["text"].strip()}”'
             # Replace newlines with spaces to prevent weird wrapping with quotes
             segments[0]['text'] = segments[0]['text'].replace('\n', ' ')

        print(f"📝 Burning Text: {segments[0]['text'][:30]}...")
        try:
            subtitle_clips = self._generate_subtitles(segments, video_clip.size)
            video_clip = video_clip.fx(fadein, 1.0)
            final_video = CompositeVideoClip([video_clip] + subtitle_clips)
        except Exception as e:
            print(f"⚠️ Subtitle Error: {e}")
            final_video = video_clip
        
        # 6. Export
        print(f"💾 Exporting to {output_path}...")
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac',
            threads=4,
            logger='bar'
        )
        print("✅ Video Export Complete!")
        return output_path

    def _generate_subtitles(self, segments, videosize):
        w, h = videosize
        clips = []
        
        for segment in segments:
            start = segment['start']
            end = segment['end']
            duration = end - start
            text = segment['text'].strip()
            
            txt_clip = TextClip(
                text, 
                fontsize=self.style['fontsize'], 
                font=self.style['font'], 
                color=self.style['color'], 
                stroke_color=self.style['stroke_color'], 
                stroke_width=self.style['stroke_width'],
                size=(w*0.90, None), # Increased width to 90% for big quotes
                method='caption',
                align='center'
            )
            
            txt_clip = txt_clip.set_position(self.style['position'])
            txt_clip = txt_clip.set_start(start).set_duration(duration)
            
            fade_dur = min(self.style['fade_duration'], duration / 3)
            txt_clip = txt_clip.fx(fadein, fade_dur)
            if duration > 1.5: 
                txt_clip = txt_clip.fx(fadeout, fade_dur)
            
            clips.append(txt_clip)
            
        return clips

# --- TEST BLOCK ---
if __name__ == "__main__":
    print("\n--- PROFESSIONAL QUOTE VIDEO TEST ---")
    os.makedirs("output", exist_ok=True)
    
    audio_path = None
    # We pass a special flag to force solid black background
    background_path = "solid_black" 

    music_files = glob.glob("assets/background_music/*.mp3")
    music_path = music_files[0] if music_files else None

    # Test Quote (No quotes needed here, the engine adds them)
    quote_text = "The only way to do great work is to love what you do. - Steve Jobs"

    engine = VideoEngine()
    output_file = "output/test_pro_quote.mp4"
    try:
        engine.create_video(
            audio_path=audio_path,
            background_path=background_path, 
            music_path=music_path, 
            output_path=output_file,
            transcription=quote_text
        )
        print(f"\n✅ SUCCESS! Check: {output_file}")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")