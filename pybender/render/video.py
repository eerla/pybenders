from moviepy import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip,
    AudioArrayClip,
    vfx,
)
from pathlib import Path
import numpy as np
from datetime import datetime


class VideoRenderer:
    def __init__(self):
        self.VIDEO_W, self.VIDEO_H = 1080, 1920
        self.FPS = 30
        self.SAFE_WIDTH = 960
        self.QUESTION_DURATION = 1
        self.CTA_DURATION = 1
        self.TOTAL_DURATION = self.QUESTION_DURATION + self.CTA_DURATION

        self.RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.RUN_DATE = datetime.now().strftime("%Y%m%d")


    def generate_day1_reel(
        self,
        question_img: Path,
        **kwargs,
    ):
        """
        Generate Day 1 reel:
        Welcome → Question → CTA
        """
        welcome_img = kwargs.get("welcome_img", None)
        cta_img = kwargs.get("cta_img", None)   
        music_path = kwargs.get("music_path", None)
        # Default CTA image if none provided
        if cta_img is None:
            cta_img = Path("output/images/cta/day1.png")

        if welcome_img is None:
            welcome_img = Path("output/images/welcome/welcome.png")
        
        if music_path is None:
            music_path = Path("pybender/assets/music/chill_loop.mp3")
        
        # --------------------------------------------------
        # Output Path (timestamped)
        # --------------------------------------------------
        out_dir = Path(f"output/reels/day1/{self.RUN_DATE}")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{self.RUN_TIMESTAMP}_day1_reel.mp4"

        # --------------------------------------------------
        # Durations
        # --------------------------------------------------
        WELCOME_DUR = 3.0
        QUESTION_DUR = 7.0
        CTA_DUR = 4.0
        FADE_DUR = 0.6

        # --------------------------------------------------
        # Welcome Clip
        # --------------------------------------------------
        welcome_clip = (
            ImageClip(str(welcome_img))
            .resized(height=self.VIDEO_H)
            .with_duration(WELCOME_DUR)
            .with_fps(self.FPS)
            .with_effects([vfx.Resize(1.02), vfx.FadeOut(FADE_DUR)])
        )

        # --------------------------------------------------
        # Question Clip
        # --------------------------------------------------
        question_clip = (
            ImageClip(str(question_img))
            .resized(height=self.VIDEO_H)
            .with_duration(QUESTION_DUR)
            .with_fps(self.FPS)
            .with_start(WELCOME_DUR - FADE_DUR)
            .with_effects([
                vfx.FadeIn(FADE_DUR),
                vfx.FadeOut(FADE_DUR)
            ])
        )


        # --------------------------------------------------
        # CTA Clip
        # --------------------------------------------------
        cta_clip = (
            ImageClip(str(cta_img))
            .resized(height=self.VIDEO_H)
            .with_duration(CTA_DUR)
            .with_fps(self.FPS)
            .with_start(WELCOME_DUR + QUESTION_DUR - (FADE_DUR * 2))
            .with_effects([vfx.FadeIn(FADE_DUR)])
        )


        # --------------------------------------------------
        # Composite
        # --------------------------------------------------
        final_video = CompositeVideoClip(
            [welcome_clip, question_clip, cta_clip],
            size=(self.VIDEO_W, self.VIDEO_H)
        ).with_duration(
            WELCOME_DUR + QUESTION_DUR + CTA_DUR
        ).with_fps(self.FPS)

        # --------------------------------------------------
        # Audio (optional)
        # --------------------------------------------------
        if music_path and music_path.exists():
            audio = (
                AudioFileClip(str(music_path))
                .subclipped(0, final_video.duration)
                .with_volume_scaled(0.35)
            )
            final_video = final_video.with_audio(audio)
        else:
            # silent track so players enable volume button
            samples = int(final_video.duration * 44100)
            silence = np.zeros((samples, 2), dtype=np.float32)
            final_video = final_video.with_audio(
                AudioArrayClip(silence, fps=44100)
            )

        # --------------------------------------------------
        # Export
        # --------------------------------------------------
        final_video.write_videofile(
            str(out_path),
            codec="libx264",
            audio_codec="aac",
            fps=self.FPS,
            preset="ultrafast",
            threads=4
        )

        print(f"✅ Day 1 reel generated at: {out_path}")


    def generate_day2_reel(
        self,
        question_img: Path,
        answer_img: Path,
        **kwargs,
    ):
        """
        Generate Day 2 reel:
        Question → Answer Reveal → CTA
        """

        cta_img = kwargs.get("cta_img", None)
        music_path = kwargs.get("music_path", None)

        # Defaults
        if cta_img is None:
            cta_img = Path("output/images/cta/day2.png")

        if music_path is None:
            music_path = Path("pybender/assets/music/chill_loop.mp3")

        # --------------------------------------------------
        # Output Path (same RUN_TIMESTAMP as Day 1)
        # --------------------------------------------------
        out_dir = Path(f"output/reels/day2/{self.RUN_DATE}")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{self.RUN_TIMESTAMP}_day2_reel.mp4"

        # --------------------------------------------------
        # Durations
        # --------------------------------------------------
        QUESTION_DUR = 3.0
        ANSWER_DUR = 5.0
        CTA_DUR = 4.0
        FADE_DUR = 0.4

        # --------------------------------------------------
        # Question Clip (short reminder)
        # --------------------------------------------------
        question_clip = (
            ImageClip(str(question_img))
            .resized(height=self.VIDEO_H)
            .with_duration(QUESTION_DUR)
            .with_fps(self.FPS)
            .with_effects([vfx.Resize(1.02), vfx.FadeOut(FADE_DUR)])
        )

        # --------------------------------------------------
        # Answer Reveal Clip (main highlight)
        # --------------------------------------------------
        answer_clip = (
            ImageClip(str(answer_img))
            .resized(height=self.VIDEO_H)
            .with_duration(ANSWER_DUR)
            .with_fps(self.FPS)
            .with_start(QUESTION_DUR - FADE_DUR)
            # subtle pop-in effect
            .with_effects([vfx.Resize(1.04)])
            .with_effects([vfx.FadeIn(FADE_DUR), vfx.FadeOut(FADE_DUR)])
        )

        # --------------------------------------------------
        # CTA Clip
        # --------------------------------------------------
        cta_clip = (
            ImageClip(str(cta_img))
            .resized(height=self.VIDEO_H)
            .with_duration(CTA_DUR)
            .with_fps(self.FPS)
            .with_start(QUESTION_DUR + ANSWER_DUR - (FADE_DUR * 2))
            .with_effects([vfx.Resize(1.02), vfx.FadeIn(FADE_DUR)])
        )

        # --------------------------------------------------
        # Composite
        # --------------------------------------------------
        final_video = CompositeVideoClip(
            [question_clip, answer_clip, cta_clip],
            size=(self.VIDEO_W, self.VIDEO_H)
        ).with_duration(
            QUESTION_DUR + ANSWER_DUR + CTA_DUR
        ).with_fps(self.FPS)

        # --------------------------------------------------
        # Audio
        # --------------------------------------------------
        if music_path and music_path.exists():
            audio = (
                AudioFileClip(str(music_path))
                .subclipped(0, final_video.duration)
                .with_volume_scaled(0.25)
            )
            final_video = final_video.with_audio(audio)
        else:
            samples = int(final_video.duration * 44100)
            silence = np.zeros((samples, 2), dtype=np.float32)
            final_video = final_video.with_audio(
                AudioArrayClip(silence, fps=44100)
            )

        # --------------------------------------------------
        # Export
        # --------------------------------------------------
        final_video.write_videofile(
            str(out_path),
            codec="libx264",
            audio_codec="aac",
            fps=self.FPS,
            preset="ultrafast",
            threads=4
        )

        print(f"✅ Day 2 reel generated at: {out_path}")


if __name__ == "__main__":
    renderer = VideoRenderer()
    import os
    import random
    from concurrent.futures import ProcessPoolExecutor

    questions_images = os.listdir("output/images/questions")
    for qi in questions_images:
        qi_path = Path("output/images/questions") / qi
        ai_path = Path("output/images/answers") / qi

        with ProcessPoolExecutor(max_workers=2) as executor: 
            future1 = executor.submit(renderer.generate_day1_reel, question_img=qi_path)
            future2 = executor.submit(renderer.generate_day2_reel, question_img=qi_path, answer_img=ai_path)
            future1.result()
            future2.result()

        print(f"Reel created successfully for {qi}")

