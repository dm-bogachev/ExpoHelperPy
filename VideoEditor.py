from moviepy import VideoFileClip, AudioFileClip
import logging
from Config import Config
import os

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

class VideoEditor:
    def __init__(self):
        Config.init()
        self.audio_path = Config.get('sound_name')

    def trim_and_add_audio(self, video_path, start_sec, end_sec, output_path):
        try:
            logger.info(f"Loading video: {video_path}")
            video_clip = VideoFileClip(video_path)

            if end_sec > video_clip.duration:
                logger.info(f"end_sec {end_sec} exceeds video duration {video_clip.duration}. Trimming to video end.")
                end_sec = video_clip.duration
            
            logger.info(f"Trimming video from {start_sec} to {end_sec} seconds")
            trimmed_clip = video_clip.subclipped(start_sec, end_sec)

            logger.info(f"Loading audio: {self.audio_path}")
            audio_clip = AudioFileClip(os.path.join("data", self.audio_path))
            audio_clip = audio_clip.subclipped(0, trimmed_clip.duration)
            
            final_clip = trimmed_clip.with_audio(audio_clip)
            logger.info(f"Writing output video to: {output_path}")
            
            final_clip.write_videofile(output_path, codec='libx264', audio_codec='aac')
            logger.info("Processing completed successfully.")
        except Exception as e:
            logger.error(f"Error during video processing: {e}")

# Пример использования
if __name__ == '__main__':
    import logging
    import os
    from Config import Config
    Config.init()
    logging.basicConfig(level=logging.INFO)
    
    editor = VideoEditor()
    editor.trim_and_add_audio("video/output.mp4", 3, 20, "video/output2.mp4")