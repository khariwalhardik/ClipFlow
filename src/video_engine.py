import os
from moviepy.editor import (
    VideoFileClip, AudioFileClip, TextClip, 
    CompositeVideoClip, CompositeAudioClip
)
from moviepy.video.fx.all import crop

class VideoEngine:
    def __init__(self):
        self.font = "Arial-Bold" # Ensure this font is on your system or use path to .ttf
        self.fontsize = 70
        self.color = 'white'
        self.stroke_color = 'black'
        self.stroke_width = 2

    def create_video(self, audio_path, background_path, music_path, output_path, transcription):
        """
        Assembles the final video from assets.
        transcription: The dictionary result from Whisper with 'segments'.
        """
        print("🎬 Starting Video Assembly...")
        
        # 1. Load Audio and Video
        voice_clip = AudioFileClip(audio_path)
        video_clip = VideoFileClip(background_path)
        
        # 2. Loop Video if it's shorter than audio
        if video_clip.duration < voice_clip.duration:
            print("🔄 Looping background video...")
            video_clip = video_clip.loop(duration=voice_clip.duration)
        else:
            video_clip = video_clip.subclip(0, voice_clip.duration)
            
        # 3. Crop to Vertical (9:16) - Center Crop
        w, h = video_clip.size
        target_ratio = 9/16
        
        # Calculate new width based on height to keep aspect ratio
        new_w = h * target_ratio
        
        # If original width is smaller than target width, we have to scale based on width? 
        # Usually Pexels videos are landscape, so we crop the center.
        if w > new_w:
            x_center = w / 2
            video_clip = crop(video_clip, width=new_w, height=h, x_center=x_center, y_center=h/2)
        
        # Resize to standard 1080x1920 just to be safe for Instagram
        video_clip = video_clip.resize(height=1920)

        # 4. Audio Mixing
        # Voice is 100% volume
        # Music is 10% volume and looped
        if music_path and os.path.exists(music_path):
            music_clip = AudioFileClip(music_path)
            # Loop music to match voice duration
            if music_clip.duration < voice_clip.duration:
                music_clip = music_clip.loop(duration=voice_clip.duration)
            else:
                music_clip = music_clip.subclip(0, voice_clip.duration)
                
            music_clip = music_clip.volumex(0.10) # 10% volume
            final_audio = CompositeAudioClip([voice_clip, music_clip])
        else:
            final_audio = voice_clip

        video_clip = video_clip.set_audio(final_audio)

        # 5. Generate Subtitles
        subtitle_clips = self._generate_subtitles(transcription['segments'], video_clip.size)
        
        # Combine everything
        final_video = CompositeVideoClip([video_clip] + subtitle_clips)
        
        # 6. Export
        print(f"💾 Exporting to {output_path}...")
        final_video.write_videofile(
            output_path, 
            fps=24, 
            codec='libx264', 
            audio_codec='aac',
            threads=4
        )
        print("✅ Video Export Complete!")
        return output_path

    def _generate_subtitles(self, segments, videosize):
        """
        Create TextClips from Whisper segments.
        """
        w, h = videosize
        clips = []
        
        for segment in segments:
            start = segment['start']
            end = segment['end']
            text = segment['text'].strip()
            
            # Create the text clip
            # We use `method='caption'` to wrap text automatically
            txt_clip = TextClip(
                text, 
                fontsize=self.fontsize, 
                font=self.font, 
                color=self.color, 
                stroke_color=self.stroke_color, 
                stroke_width=self.stroke_width,
                size=(w*0.8, None), # 80% of width, auto height
                method='caption'
            )
            
            txt_clip = txt_clip.set_position(('center', 'center'))
            txt_clip = txt_clip.set_start(start).set_end(end)
            
            clips.append(txt_clip)
            
        return clips

# --- Testing Block ---
if __name__ == "__main__":
    # To test this, you need actual files.
    # It's better to test via main.py in the next step.
    print("Run main.py to test the full flow.")