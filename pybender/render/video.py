from moviepy import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip,
    AudioArrayClip,
    vfx,
)
from pathlib import Path
from typing import List, Dict, Any
import numpy as np
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed


class VideoRenderer:
    def __init__(self):
        self.VIDEO_W, self.VIDEO_H = 1080, 1920
        self.FPS = 30
        self.SAFE_WIDTH = 960

        self.RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.RUN_DATE = datetime.now().strftime("%Y%m%d")

    @staticmethod
    def extract_question_id_from_image(path: Path) -> str:
        """
        Extract question_id from image filename.
        Example:
        2025-12-24_175633_q01_question.png → 2025-12-24_175633_q01
        """
        return path.stem.replace("_question", "")


    def generate_day1_reel(
        self,
        question_img: Path,
        **kwargs,
    ):
        """
        Generate Day 1 reel:
        Welcome → Question → CTA
        """
        welcome_img = kwargs.get("welcome_img") or Path("output/images/welcome/welcome.png")
        cta_img = kwargs.get("cta_img") or Path("output/images/cta/day1.png")   
        music_path = kwargs.get("music_path") or Path("pybender/assets/music/chill_loop.mp3")
        # --------------------------------------------------
        # Derive question_id from image filename
        # --------------------------------------------------
        question_id = self.extract_question_id_from_image(question_img)
        # --------------------------------------------------
        # Output Path (timestamped)
        # --------------------------------------------------
        out_dir = Path(f"output/reels/day1/{self.RUN_DATE}")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{question_id}_day1.mp4"

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

        cta_img = kwargs.get("cta_img") or Path("output/images/cta/day2.png")
        music_path = kwargs.get("music_path") or Path("pybender/assets/music/chill_loop.mp3")

        # --------------------------------------------------
        # Derive question_id from image filename
        # --------------------------------------------------
        question_id = self.extract_question_id_from_image(question_img)
        # --------------------------------------------------
        # Output Path (same RUN_TIMESTAMP as Day 1)
        # --------------------------------------------------
        out_dir = Path(f"output/reels/day2/{self.RUN_DATE}")
        out_dir.mkdir(parents=True, exist_ok=True)
        out_path = out_dir / f"{question_id}_day2.mp4"

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


    @staticmethod
    def load_metadata(metadata_path: Path) -> dict:
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        with open(metadata_path, "r") as f:
            metadata = json.load(f)
        
        return metadata

    @staticmethod
    def get_question_assets(metadata: Dict[str, Any]) -> List[Dict[str, Path]]:
        """
        Extract image asset paths for each question.
        """
        assets = []

        for q in metadata.get("questions", []):
            q_assets = q.get("assets", {})

            assets.append({
                "question_id": q["question_id"],
                "title": q["title"],
                "question_image": Path(q_assets["question_image"]),
                "answer_image": Path(q_assets["answer_image"]),
                "single_post_image": Path(q_assets["single_post_image"]),
            })

        return assets 

    # --------------------------------------------------
    # Worker for one question (Day1 + Day2 in parallel)
    # --------------------------------------------------
    def process_question(self, asset: dict) -> dict:
        question_img = asset["question_image"]
        answer_img = asset["answer_image"]

        question_id = self.extract_question_id_from_image(Path(question_img))

        # Output paths (must match generate_* logic)
        day1_path = Path(f"output/reels/day1/{self.RUN_DATE}/{question_id}_day1.mp4")
        day2_path = Path(f"output/reels/day2/{self.RUN_DATE}/{question_id}_day2.mp4")

        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(
                    self.generate_day1_reel,
                    question_img=Path(question_img)
                ),
                executor.submit(
                    self.generate_day2_reel,
                    question_img=Path(question_img),
                    answer_img=Path(answer_img)
                ),
            ]

            # Ensure both complete (and raise if any fail)
            for f in futures:
                f.result()

        return {
            "question_id": question_id,
            "reels": {
                "day1": str(day1_path),
                "day2": str(day2_path),
            }
        }

    def main(self, metadata_path: Path) -> Path:
        
        if not metadata_path.exists():
            raise FileNotFoundError(f"Metadata file not found: {metadata_path}")
        
        metadata = self.load_metadata(metadata_path)
        assets = self.get_question_assets(metadata)

         # --------------------------------------------------
        # Run all questions in parallel
        # --------------------------------------------------
        reel_results = []

        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(self.process_question, asset) for asset in assets]

            for future in as_completed(futures):
                result = future.result()
                reel_results.append(result)
                print(f"✅ Reels generated for {result['question_id']}")

        # --------------------------------------------------
        # Update metadata with reels section
        # --------------------------------------------------
        reels_map = {r["question_id"]: r["reels"] for r in reel_results}

        for q in metadata["questions"]:
            qid = q["question_id"]
            if qid in reels_map:
                q.setdefault("assets", {})
                q["assets"]["reels"] = reels_map[qid]

        print("📦 All reels generated")
        # --------------------------------------------------
        # Write metadata back
        # --------------------------------------------------
        with open(metadata_path, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)

        print("📦 Metadata updated with reel paths")

        return metadata_path



