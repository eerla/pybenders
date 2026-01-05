import json
import logging
import os
import gc
import random
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import numpy as np
from moviepy.audio.AudioClip import AudioArrayClip
from moviepy.editor import (
    AudioFileClip,
    CompositeVideoClip,
    ImageClip,
    vfx,
)

from pybender.config.logging_config import setup_logging


logger = logging.getLogger(__name__)


def _ensure_logging_configured() -> None:
    if not logging.getLogger().handlers:
        setup_logging()


class VideoRenderer:
    def __init__(self):
        _ensure_logging_configured()
        self.VIDEO_W, self.VIDEO_H = 1080, 1920
        self.FPS = 30
        self.SAFE_WIDTH = 960
        # self.BASE_DIR = Path("output_1") # local output path
        self.BASE_DIR = Path(r"G:\My Drive\output") # Change to google drive path
        self.RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.RUN_DATE = datetime.now().strftime("%Y%m%d")
        self.ASSETS_DIR = Path("pybender/assets")

    def _get_random_audio_clip(self) -> Optional[Path]:
        """
        Select a random audio clip from the audio_clips folder.
        
        Returns:
            Path to random audio clip, or None if folder is empty
        """
        audio_dir = self.ASSETS_DIR / "music" / "audio_clips"
        
        if not audio_dir.exists():
            logger.warning(f"Audio clips directory not found: {audio_dir}")
            return None
        
        audio_files = [f for f in audio_dir.glob("*") if f.is_file() and f.suffix.lower() in [".mp3", ".wav", ".m4a", ".aac"]]
        
        if not audio_files:
            logger.warning(f"No audio clips found in: {audio_dir}")
            return None
        
        selected_clip = random.choice(audio_files)
        logger.info(f"🎵 Selected random audio clip: {selected_clip.name}")
        return selected_clip

    @staticmethod
    def extract_question_id_from_image(path: Path) -> str:
        """
        Extract question_id from image filename.
        Example:
        2025-12-24_175633_q01_question.png → 2025-12-24_175633_q01
        """
        return path.stem.replace("_question", "")

    @staticmethod
    def load_metadata(metadata_path: Path) -> dict:
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        return metadata

    def get_question_assets(self, metadata: dict) -> list[dict]:
        """
        Extract question image paths from metadata.
        Returns list of asset dicts (one per question).
        
        All content types now use nested reel structure:
        - Technical (python, js, etc): question_image, answer_image + transitions
        - Mind benders: welcome, question, hint, answer, cta
        - Finance: welcome, insight, explanation, example, action, cta
        - Psychology: welcome, statement, explanation, example, application, cta
        """
        assets = []
        subject = metadata.get("subject", "")
        theme = metadata.get("theme")
        
        for q in metadata["questions"]:
            reel_assets = q.get("assets", {}).get("reel", {})
            
            asset_dict = {
                "subject": subject,
                "question_id": q["question_id"],
                "theme": theme,
            }
            
            # Finance: has insight_image
            if "insight_image" in reel_assets:
                asset_dict.update({
                    "welcome_image": reel_assets["welcome_image"],
                    "insight_image": reel_assets["insight_image"],
                    "explanation_image": reel_assets["explanation_image"],
                    "example_image": reel_assets["example_image"],
                    "action_image": reel_assets["action_image"],
                    "cta_image": reel_assets["cta_image"],
                    "type": "finance",
                })
            # Psychology: has statement_image
            elif "statement_image" in reel_assets:
                asset_dict.update({
                    "welcome_image": reel_assets["welcome_image"],
                    "statement_image": reel_assets["statement_image"],
                    "explanation_image": reel_assets["explanation_image"],
                    "example_image": reel_assets["example_image"],
                    "application_image": reel_assets["application_image"],
                    "cta_image": reel_assets["cta_image"],
                    "type": "psychology",
                })
            # Mind benders: has hint_image
            elif "hint_image" in reel_assets:
                asset_dict.update({
                    "welcome_image": reel_assets["welcome_image"],
                    "question_image": reel_assets["question_image"],
                    "hint_image": reel_assets["hint_image"],
                    "answer_image": reel_assets["answer_image"],
                    "cta_image": reel_assets["cta_image"],
                    "type": "mind_benders",
                })
            # Technical: only question_image + answer_image
            else:
                asset_dict.update({
                    "question_image": reel_assets["question_image"],
                    "answer_image": reel_assets["answer_image"],
                    "type": "technical",
                })
            
            assets.append(asset_dict)
        
        return assets 

    def generate_combined_reel(
        self,
        welcome_img: Path,
        question_img: Path,
        transition_imgs,
        answer_img: Path,
        cta_img: Path,
        out_path: Path,
        **kwargs,
        ):
        """
        Generate combined reel with complete story arc.
        
        Structure:
        - Welcome (2s) with fade-out
        - Question (7s) with fade-in/out
        - Transition countdown (2s total): base (0.6s) → 2 (0.6s) → 1 (0.6s) → ready (0.2s)
        - Answer (7s) with fade-in/out
        - CTA (2s) with fade-in
        
        Total: 20 seconds (optimal for Reels)
        
        Audio: Randomly selected from audio_clips folder
        """
        music_path = self._get_random_audio_clip()
        
        # --------------------------------------------------
        # Setup temp directory for MoviePy
        # --------------------------------------------------
        subject = out_path.parent.parent.name  # Extract subject from path
        temp_dir = (self.BASE_DIR / subject / "temp").absolute()
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save and set temp directory for Python's tempfile module
        original_tempdir = tempfile.tempdir
        tempfile.tempdir = str(temp_dir)
        
        # --------------------------------------------------
        # Durations (in seconds)
        # --------------------------------------------------
        WELCOME_DUR = 2.0
        QUESTION_DUR = 7.0
        TRANSITION_DUR = 4.8
        ANSWER_DUR = 7.0
        CTA_DUR = 2.0
        FADE_DUR = 0.4
        
        # --------------------------------------------------
        # Clips
        # --------------------------------------------------
        
        # 1. Welcome Clip (0-2s)
        welcome_clip = (
            ImageClip(str(welcome_img))
            .resize(height=self.VIDEO_H)
            .set_duration(WELCOME_DUR)
            .set_fps(self.FPS)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # 2. Question Clip (1.6-8.6s, overlaps with welcome fadeout)
        question_clip = (
            ImageClip(str(question_img))
            .resize(height=self.VIDEO_H)
            .set_duration(QUESTION_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR - FADE_DUR)
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # 3. Transition Clips with Countdown (8.2-10.2s, total 2s)
        # Split transition_img into 4 clips: base (0.6s), 2 (0.6s), 1 (0.6s), ready (0.2s)
        
        # Derive transition image paths from provided transition_imgs
        if isinstance(transition_imgs, dict):
            t_base_path = transition_imgs.get("base", Path("pybender/assets/backgrounds/transition_base.png"))
            t_2_path = transition_imgs.get("2", Path("pybender/assets/backgrounds/transition_2.png"))
            t_1_path = transition_imgs.get("1", Path("pybender/assets/backgrounds/transition_1.png"))
            t_ready_path = transition_imgs.get("ready", Path("pybender/assets/backgrounds/transition_ready.png"))
        else:
            # If a single Path/string is provided, derive siblings
            base_stem = str(transition_imgs).replace(".png", "").replace("_2", "").replace("_1", "").replace("_ready", "")
            t_base_path = Path(base_stem + "_base.png")
            t_2_path = Path(base_stem + "_2.png")
            t_1_path = Path(base_stem + "_1.png")
            t_ready_path = Path(base_stem + "_ready.png")
        
        transition_start = WELCOME_DUR + QUESTION_DUR - (FADE_DUR * 2)
        
        t_base_clip = (
            ImageClip(str(t_base_path))
            .resize(height=self.VIDEO_H)
            .set_duration(1.3)
            .set_fps(self.FPS)
            .set_start(transition_start)
            .fx(vfx.fadein, 0.4)
            .fx(vfx.fadeout, 0.4)
        )
        
        t_2_clip = (
            ImageClip(str(t_2_path))
            .resize(height=self.VIDEO_H)
            .set_duration(1.3)
            .set_fps(self.FPS)
            .set_start(transition_start + 1.3)
            .fx(vfx.fadein, 0.4)
            .fx(vfx.fadeout, 0.4)
        )
        
        t_1_clip = (
            ImageClip(str(t_1_path))
            .resize(height=self.VIDEO_H)
            .set_duration(1.3)
            .set_fps(self.FPS)
            .set_start(transition_start + 2.6)
            .fx(vfx.fadein, 0.4)
            .fx(vfx.fadeout, 0.4)
        )
        
        t_ready_clip = (
            ImageClip(str(t_ready_path))
            .resize(height=self.VIDEO_H)
            .set_duration(0.9)
            .set_fps(self.FPS)
            .set_start(transition_start + 3.9)
            .fx(vfx.fadein, 0.4)
        )
        
        # 4. Answer Clip (9.8-16.8s)
        answer_clip = (
            ImageClip(str(answer_img))
            .resize(height=self.VIDEO_H)
            .set_duration(ANSWER_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + QUESTION_DUR + TRANSITION_DUR - (FADE_DUR * 2))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # 5. CTA Clip (16.4-18.4s)
        cta_start = WELCOME_DUR + QUESTION_DUR + TRANSITION_DUR + ANSWER_DUR - (FADE_DUR * 4)  # 16.4s with 0.4s overlaps
        cta_clip = (
            ImageClip(str(cta_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CTA_DUR)
            .set_fps(self.FPS)
            .set_start(cta_start)
            .fx(vfx.fadein, FADE_DUR)
        )
        
        # --------------------------------------------------
        # Composite
        # --------------------------------------------------
        total_duration = max(
            welcome_clip.end,
            question_clip.end,
            t_base_clip.end,
            t_2_clip.end,
            t_1_clip.end,
            t_ready_clip.end,
            answer_clip.end,
            cta_clip.end,
        )
        
        final_video = CompositeVideoClip(
            [welcome_clip, question_clip, t_base_clip, t_2_clip, t_1_clip, t_ready_clip, answer_clip, cta_clip],
            size=(self.VIDEO_W, self.VIDEO_H)
        ).set_duration(total_duration).set_fps(self.FPS)
        
        # --------------------------------------------------
        # Audio
        # --------------------------------------------------
        audio_clip = None
        if music_path and music_path.exists():
            audio_clip = AudioFileClip(str(music_path))
            audio = (
                audio_clip
                .subclip(0, final_video.duration)
                .volumex(0.30)
            )
            final_video = final_video.set_audio(audio)
        else:
            # Silent track
            samples = int(final_video.duration * 44100)
            silence = np.zeros((samples, 2), dtype=np.float32)
            final_video = final_video.set_audio(
                AudioArrayClip(silence, fps=44100)
            )
        
        # --------------------------------------------------
        # Export
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        # Collect all clips for cleanup
        all_clips = [welcome_clip, question_clip, t_base_clip, t_2_clip, t_1_clip, t_ready_clip, answer_clip, cta_clip]
        
        try:
            final_video.write_videofile(
                str(out_path),
                codec="libx264",
                audio_codec="aac",
                fps=self.FPS,
                preset="ultrafast",
                threads=1  # Reduced for stability
            )
            logger.info("✅ Combined reel generated at: %s", out_path)
        finally:
             # CRITICAL: Clean up MoviePy resources to free memory
            try:
                if audio_clip:
                    audio_clip.close()
                for clip in all_clips:
                    clip.close()
                final_video.close()
            except Exception as e:
                logger.warning(f"Error during clip cleanup: {e}")
            finally:
                del all_clips, final_video, audio_clip
                gc.collect()  # Force garbage collection
                
                # Restore original temp directory
                tempfile.tempdir = original_tempdir

    def generate_mind_benders_reel(
        self,
        welcome_img: Path,
        question_img: Path,
        hint_img: Path,
        answer_img: Path,
        cta_img: Path,
        out_path: Path,
        music_path: Optional[Path] = None,
    ):
        """
        Generate mind_benders reel with 5-image sequence (no transitions).
        
        Sequence:
        - Welcome: 2s
        - Question: 5s  
        - Hint: 3s
        - Answer: 6s
        - CTA: 2s
        Total: 18s
        
        Audio: Randomly selected from audio_clips folder
        """
        logger.info("🎬 Generating mind_benders reel: %s", out_path.name)
        
        # Get random audio clip (ignore music_path parameter if provided)
        music_path = self._get_random_audio_clip()
        
        # --------------------------------------------------
        # Setup temp directory for MoviePy
        # --------------------------------------------------
        subject = out_path.parent.parent.name  # Extract subject from path
        temp_dir = (self.BASE_DIR / subject / "temp").absolute()
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save and set temp directory for Python's tempfile module
        original_tempdir = tempfile.tempdir
        tempfile.tempdir = str(temp_dir)
        
        # --------------------------------------------------
        # Timing Configuration
        # --------------------------------------------------
        WELCOME_DUR = 2.0
        QUESTION_DUR = 5.0
        HINT_DUR = 3.0
        ANSWER_DUR = 6.0
        CTA_DUR = 2.0
        FADE_DUR = 0.2
        
        # --------------------------------------------------
        # 1. Welcome Clip (0-2s)
        # --------------------------------------------------
        welcome_clip = (
            ImageClip(str(welcome_img))
            .resize(height=self.VIDEO_H)
            .set_duration(WELCOME_DUR)
            .set_fps(self.FPS)
            .set_start(0)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 2. Question Clip (1.8-6.8s with overlap)
        # --------------------------------------------------
        question_clip = (
            ImageClip(str(question_img))
            .resize(height=self.VIDEO_H)
            .set_duration(QUESTION_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR - FADE_DUR)
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 3. Hint Clip (6.6-9.6s with overlap)
        # --------------------------------------------------
        hint_clip = (
            ImageClip(str(hint_img))
            .resize(height=self.VIDEO_H)
            .set_duration(HINT_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + QUESTION_DUR - (FADE_DUR * 2))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 4. Answer Clip (9.4-15.4s with overlap)
        # --------------------------------------------------
        answer_clip = (
            ImageClip(str(answer_img))
            .resize(height=self.VIDEO_H)
            .set_duration(ANSWER_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + QUESTION_DUR + HINT_DUR - (FADE_DUR * 3))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 5. CTA Clip (15.2-17.2s with overlap)
        # --------------------------------------------------
        cta_clip = (
            ImageClip(str(cta_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CTA_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + QUESTION_DUR + HINT_DUR + ANSWER_DUR - (FADE_DUR * 4))
            .fx(vfx.fadein, FADE_DUR)
        )
        
        # --------------------------------------------------
        # Composite
        # --------------------------------------------------
        total_duration = max(
            welcome_clip.end,
            question_clip.end,
            hint_clip.end,
            answer_clip.end,
            cta_clip.end,
        )
        
        final_video = CompositeVideoClip(
            [welcome_clip, question_clip, hint_clip, answer_clip, cta_clip],
            size=(self.VIDEO_W, self.VIDEO_H)
        ).set_duration(total_duration).set_fps(self.FPS)
        
        # --------------------------------------------------
        # Audio
        # --------------------------------------------------
        audio_clip = None
        if music_path and music_path.exists():
            audio_clip = AudioFileClip(str(music_path))
            audio = (
                audio_clip
                .subclip(0, final_video.duration)
                .volumex(0.30)
            )
            final_video = final_video.set_audio(audio)
        else:
            # Silent track
            samples = int(final_video.duration * 44100)
            silence = np.zeros((samples, 2), dtype=np.float32)
            final_video = final_video.set_audio(
                AudioArrayClip(silence, fps=44100)
            )
        
        # --------------------------------------------------
        # Export
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        all_clips = [welcome_clip, question_clip, hint_clip, answer_clip, cta_clip]
        
        try:
            final_video.write_videofile(
                str(out_path),
                codec="libx264",
                audio_codec="aac",
                fps=self.FPS,
                preset="ultrafast",
                threads=1
            )
            logger.info("✅ Mind benders reel generated at: %s", out_path)
        finally:
            # CRITICAL: Clean up MoviePy resources
            try:
                if audio_clip:
                    audio_clip.close()
                for clip in all_clips:
                    clip.close()
                final_video.close()
            except Exception as e:
                logger.warning(f"Error during clip cleanup: {e}")
            finally:
                del all_clips, final_video, audio_clip
                gc.collect()
                
                # Restore original temp directory
                tempfile.tempdir = original_tempdir

    def generate_finance_reel(
        self,
        welcome_img: Path,
        insight_img: Path,
        explanation_img: Path,
        example_img: Path,
        action_img: Path,
        cta_img: Path,
        out_path: Path,
    ):
        """
        Generate finance reel with 6-card sequence.
        
        Sequence:
        - Welcome: 2s
        - Insight: 4s
        - Explanation: 4s
        - Example: 4s
        - Action: 4s
        - CTA: 2s
        Total: 20s
        
        Audio: Randomly selected from audio_clips folder
        """
        logger.info("💰 Generating finance reel: %s", out_path.name)
        
        # Get random audio clip
        music_path = self._get_random_audio_clip()
        
        # --------------------------------------------------
        # Setup temp directory for MoviePy
        # --------------------------------------------------
        subject = out_path.parent.parent.name  # Extract subject from path
        temp_dir = (self.BASE_DIR / subject / "temp").absolute()
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save and set temp directory for Python's tempfile module
        original_tempdir = tempfile.tempdir
        tempfile.tempdir = str(temp_dir)
        
        # --------------------------------------------------
        # Timing Configuration
        # --------------------------------------------------
        WELCOME_DUR = 2.0
        CARD_DUR = 4.0
        CTA_DUR = 2.0
        FADE_DUR = 0.3
        
        # --------------------------------------------------
        # 1. Welcome Clip (0-2s)
        # --------------------------------------------------
        welcome_clip = (
            ImageClip(str(welcome_img))
            .resize(height=self.VIDEO_H)
            .set_duration(WELCOME_DUR)
            .set_fps(self.FPS)
            .set_start(0)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 2. Insight Clip (1.7-5.7s with overlap)
        # --------------------------------------------------
        insight_clip = (
            ImageClip(str(insight_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR - FADE_DUR)
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 3. Explanation Clip (5.4-9.4s with overlap)
        # --------------------------------------------------
        explanation_clip = (
            ImageClip(str(explanation_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + CARD_DUR - (FADE_DUR * 2))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 4. Example Clip (9.1-13.1s with overlap)
        # --------------------------------------------------
        example_clip = (
            ImageClip(str(example_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + (CARD_DUR * 2) - (FADE_DUR * 3))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 5. Action Clip (12.8-16.8s with overlap)
        # --------------------------------------------------
        action_clip = (
            ImageClip(str(action_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + (CARD_DUR * 3) - (FADE_DUR * 4))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 6. CTA Clip (16.5-18.5s with overlap)
        # --------------------------------------------------
        cta_clip = (
            ImageClip(str(cta_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CTA_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + (CARD_DUR * 4) - (FADE_DUR * 5))
            .fx(vfx.fadein, FADE_DUR)
        )
        
        # --------------------------------------------------
        # Composite
        # --------------------------------------------------
        total_duration = max(
            welcome_clip.end,
            insight_clip.end,
            explanation_clip.end,
            example_clip.end,
            action_clip.end,
            cta_clip.end,
        )
        
        final_video = CompositeVideoClip(
            [welcome_clip, insight_clip, explanation_clip, example_clip, action_clip, cta_clip],
            size=(self.VIDEO_W, self.VIDEO_H)
        ).set_duration(total_duration).set_fps(self.FPS)
        
        # --------------------------------------------------
        # Audio
        # --------------------------------------------------
        audio_clip = None
        if music_path and music_path.exists():
            audio_clip = AudioFileClip(str(music_path))
            audio = (
                audio_clip
                .subclip(0, final_video.duration)
                .volumex(0.30)
            )
            final_video = final_video.set_audio(audio)
        else:
            # Silent track
            samples = int(final_video.duration * 44100)
            silence = np.zeros((samples, 2), dtype=np.float32)
            final_video = final_video.set_audio(
                AudioArrayClip(silence, fps=44100)
            )
        
        # --------------------------------------------------
        # Export
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        all_clips = [welcome_clip, insight_clip, explanation_clip, example_clip, action_clip, cta_clip]
        
        try:
            final_video.write_videofile(
                str(out_path),
                codec="libx264",
                audio_codec="aac",
                fps=self.FPS,
                preset="ultrafast",
                threads=1
            )
            logger.info("✅ Finance reel generated at: %s", out_path)
        finally:
            # CRITICAL: Clean up MoviePy resources
            try:
                if audio_clip:
                    audio_clip.close()
                for clip in all_clips:
                    clip.close()
                final_video.close()
            except Exception as e:
                logger.warning(f"Error during clip cleanup: {e}")
            finally:
                del all_clips, final_video, audio_clip
                gc.collect()
                
                # Restore original temp directory
                tempfile.tempdir = original_tempdir

    def generate_psychology_reel(
        self,
        welcome_img: Path,
        statement_img: Path,
        explanation_img: Path,
        example_img: Path,
        application_img: Path,
        cta_img: Path,
        out_path: Path,
    ):
        """
        Generate psychology reel with 6-card sequence.
        
        Sequence:
        - Welcome: 2s
        - Statement: 4s
        - Explanation: 4s
        - Example: 4s
        - Application: 4s
        - CTA: 2s
        Total: 20s
        
        Audio: Randomly selected from audio_clips folder
        """
        logger.info("🧠 Generating psychology reel: %s", out_path.name)
        
        # Get random audio clip
        music_path = self._get_random_audio_clip()
        
        # --------------------------------------------------
        # Setup temp directory for MoviePy
        # --------------------------------------------------
        subject = out_path.parent.parent.name  # Extract subject from path
        temp_dir = (self.BASE_DIR / subject / "temp").absolute()
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        # Save and set temp directory for Python's tempfile module
        original_tempdir = tempfile.tempdir
        tempfile.tempdir = str(temp_dir)
        
        # --------------------------------------------------
        # Timing Configuration
        # --------------------------------------------------
        WELCOME_DUR = 2.0
        CARD_DUR = 4.0
        CTA_DUR = 2.0
        FADE_DUR = 0.3
        
        # --------------------------------------------------
        # 1. Welcome Clip (0-2s)
        # --------------------------------------------------
        welcome_clip = (
            ImageClip(str(welcome_img))
            .resize(height=self.VIDEO_H)
            .set_duration(WELCOME_DUR)
            .set_fps(self.FPS)
            .set_start(0)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 2. Statement Clip (1.7-5.7s with overlap)
        # --------------------------------------------------
        statement_clip = (
            ImageClip(str(statement_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR - FADE_DUR)
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 3. Explanation Clip (5.4-9.4s with overlap)
        # --------------------------------------------------
        explanation_clip = (
            ImageClip(str(explanation_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + CARD_DUR - (FADE_DUR * 2))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 4. Example Clip (9.1-13.1s with overlap)
        # --------------------------------------------------
        example_clip = (
            ImageClip(str(example_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + (CARD_DUR * 2) - (FADE_DUR * 3))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 5. Application Clip (12.8-16.8s with overlap)
        # --------------------------------------------------
        application_clip = (
            ImageClip(str(application_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CARD_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + (CARD_DUR * 3) - (FADE_DUR * 4))
            .fx(vfx.fadein, FADE_DUR)
            .fx(vfx.fadeout, FADE_DUR)
        )
        
        # --------------------------------------------------
        # 6. CTA Clip (16.5-18.5s with overlap)
        # --------------------------------------------------
        cta_clip = (
            ImageClip(str(cta_img))
            .resize(height=self.VIDEO_H)
            .set_duration(CTA_DUR)
            .set_fps(self.FPS)
            .set_start(WELCOME_DUR + (CARD_DUR * 4) - (FADE_DUR * 5))
            .fx(vfx.fadein, FADE_DUR)
        )
        
        # --------------------------------------------------
        # Composite
        # --------------------------------------------------
        total_duration = max(
            welcome_clip.end,
            statement_clip.end,
            explanation_clip.end,
            example_clip.end,
            application_clip.end,
            cta_clip.end,
        )
        
        final_video = CompositeVideoClip(
            [welcome_clip, statement_clip, explanation_clip, example_clip, application_clip, cta_clip],
            size=(self.VIDEO_W, self.VIDEO_H)
        ).set_duration(total_duration).set_fps(self.FPS)
        
        # --------------------------------------------------
        # Audio
        # --------------------------------------------------
        audio_clip = None
        if music_path and music_path.exists():
            audio_clip = AudioFileClip(str(music_path))
            audio = (
                audio_clip
                .subclip(0, final_video.duration)
                .volumex(0.30)
            )
            final_video = final_video.set_audio(audio)
        else:
            # Silent track
            samples = int(final_video.duration * 44100)
            silence = np.zeros((samples, 2), dtype=np.float32)
            final_video = final_video.set_audio(
                AudioArrayClip(silence, fps=44100)
            )
        
        # --------------------------------------------------
        # Export
        # --------------------------------------------------
        out_path.parent.mkdir(parents=True, exist_ok=True)
        all_clips = [welcome_clip, statement_clip, explanation_clip, example_clip, application_clip, cta_clip]
        
        try:
            final_video.write_videofile(
                str(out_path),
                codec="libx264",
                audio_codec="aac",
                fps=self.FPS,
                preset="ultrafast",
                threads=1
            )
            logger.info("✅ Psychology reel generated at: %s", out_path)
        finally:
            # CRITICAL: Clean up MoviePy resources
            try:
                if audio_clip:
                    audio_clip.close()
                for clip in all_clips:
                    clip.close()
                final_video.close()
            except Exception as e:
                logger.warning(f"Error during clip cleanup: {e}")
            finally:
                del all_clips, final_video, audio_clip
                gc.collect()
                
                # Restore original temp directory
                tempfile.tempdir = original_tempdir

    def process_question_v2(self, asset: dict) -> dict:
        """
        Generate single combined reel per question.
        
        Supports:
        - Technical content: 2 images + transitions (question, answer)
        - Mind benders: 5 images, no transitions (welcome, question, hint, answer, cta)
        - Finance: 6 cards (welcome, insight, explanation, example, action, cta)
        - Psychology: 6 cards (welcome, statement, explanation, example, application, cta)
        
        Output structure:
        output/
        └─ {subject}/
            └─ reels/
                └─ {question_id}.mp4
        """
        subject = asset["subject"]
        question_id = asset["question_id"]
        content_type = asset.get("type", "technical")
        
        # Output path
        combined_path = self.BASE_DIR / subject / "reels" / f"{question_id}.mp4"
        
        # Route to appropriate renderer based on content type
        if content_type == "finance":
            # Finance: 6-card sequence
            self.generate_finance_reel(
                welcome_img=Path(asset["welcome_image"]),
                insight_img=Path(asset["insight_image"]),
                explanation_img=Path(asset["explanation_image"]),
                example_img=Path(asset["example_image"]),
                action_img=Path(asset["action_image"]),
                cta_img=Path(asset["cta_image"]),
                out_path=combined_path
            )
        elif content_type == "psychology":
            # Psychology: 6-card sequence
            self.generate_psychology_reel(
                welcome_img=Path(asset["welcome_image"]),
                statement_img=Path(asset["statement_image"]),
                explanation_img=Path(asset["explanation_image"]),
                example_img=Path(asset["example_image"]),
                application_img=Path(asset["application_image"]),
                cta_img=Path(asset["cta_image"]),
                out_path=combined_path
            )
        elif content_type == "mind_benders":
            # Mind benders: 5-image sequence, no transitions
            self.generate_mind_benders_reel(
                welcome_img=Path(asset["welcome_image"]),
                question_img=Path(asset["question_image"]),
                hint_img=Path(asset["hint_image"]),
                answer_img=Path(asset["answer_image"]),
                cta_img=Path(asset["cta_image"]),
                out_path=combined_path
            )
        else:
            # Default: Technical content (2 images + transitions)
            question_img = asset["question_image"]
            answer_img = asset["answer_image"]
            transition_img_base = self.ASSETS_DIR / "backgrounds" / "transitions"
            welcome_img = self.BASE_DIR / subject / "images" / "welcome.png"
            cta_img = self.BASE_DIR / subject / "images" / "cta.png"
            transition_imgs = {
                "base": transition_img_base / "transition_base.png",
                "2": transition_img_base / "transition_2.png",
                "1": transition_img_base / "transition_1.png",
                "ready": transition_img_base / "transition_ready.png",
            }
            
            self.generate_combined_reel(
                welcome_img=welcome_img,
                question_img=Path(question_img),
                transition_imgs=transition_imgs,
                answer_img=Path(answer_img),
                cta_img=cta_img,
                out_path=combined_path
            )
        
        return {
            "question_id": question_id,
            "reel": str(combined_path)
        }

    def main(self, metadata_path: Path) -> Path:
        """
        Generate combined reels using new single-video strategy.
        
        Workflow:
        1. Load metadata with question images
        2. Generate transition image (one-time)
        3. Process all questions in parallel (each creates 1 combined reel)
        4. Update metadata with reel paths
        """
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        metadata = self.load_metadata(metadata_path)
        assets = self.get_question_assets(metadata)
        # subject = metadata.get("subject", "")
                
        # --------------------------------------------------
        # Generate combined reels in parallel
        # --------------------------------------------------
        reel_results = []
        
        with ThreadPoolExecutor(max_workers=2) as executor:  # Reduced from 4 for stability
            futures = [executor.submit(self.process_question_v2, asset) for asset in assets]
            
            for future in as_completed(futures):
                result = future.result()
                reel_results.append(result)
                logger.info("✅ Combined reel generated for %s", result["question_id"])
        
        # --------------------------------------------------
        # Update metadata with reel paths
        # --------------------------------------------------
        reels_map = {r["question_id"]: r["reel"] for r in reel_results}
        
        for q in metadata["questions"]:
            qid = q["question_id"]
            if qid in reels_map:
                q.setdefault("assets", {})
                q["assets"]["combined_reel"] = reels_map[qid]
        
        # --------------------------------------------------
        # Write metadata back
        # --------------------------------------------------
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        
        logger.info("📦 All combined reels generated (%s total)", len(reel_results))
        logger.info("📦 Metadata updated with combined reel paths")
        
        return metadata_path


# if __name__ == "__main__":
#     import sys
#     renderer = VideoRenderer()

#     metadata = sys.argv[1] if len(sys.argv) > 1 else ""
#     if not metadata:
#         logger.error("❌ Please provide the path to the metadata JSON file as an argument.")
#     else:
#         metadata_path = Path(metadata)
#         if not metadata_path.exists():
#             logger.error("❌ Metadata file not found at: %s", metadata_path)
#         else:
#             renderer.main(metadata_path)