from moviepy import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip,
    AudioArrayClip,
    vfx,
)
from pathlib import Path
import numpy as np

VIDEO_W, VIDEO_H = 1080, 1920
FPS = 30
SAFE_WIDTH = 960
QUESTION_DURATION = 1
CTA_DURATION = 1
TOTAL_DURATION = QUESTION_DURATION + CTA_DURATION


def create_question_reel(
    question_image: Path,
    music_path: Path,
    output_path: Path
):
    # --------------------------------------------------
    # QUESTION CLIP
    # --------------------------------------------------
    BG_COLOR = (9, 12, 24)
    
    base_img = ImageClip(str(question_image))
    scale = min(VIDEO_W / base_img.w, (VIDEO_H - 260) / base_img.h)
    fg_q = (
        base_img
        .resized(scale)
        .with_duration(QUESTION_DURATION)
        .with_position(("center", 340))
    )

    bg_array = np.full((VIDEO_H, VIDEO_W, 3), BG_COLOR, dtype=np.uint8)
    bg_color = ImageClip(bg_array).with_duration(QUESTION_DURATION)
    
    question_clip = CompositeVideoClip(
        [bg_color, fg_q],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(QUESTION_DURATION)

    # --------------------------------------------------
    # CTA CLIP (uses existing image)
    # --------------------------------------------------
    cta_image_path = Path("pybender/assets/backgrounds/cta.png")
    
    cta_img = ImageClip(str(cta_image_path))
    cta_img = (
        cta_img
        .resized((VIDEO_W, VIDEO_H))
        .with_duration(CTA_DURATION)
    )
    
    cta_clip = CompositeVideoClip(
        [cta_img],
        size=(VIDEO_W, VIDEO_H)
    ).with_start(QUESTION_DURATION)

    # --------------------------------------------------
    # FINAL COMPOSITION
    # --------------------------------------------------
    final_video = CompositeVideoClip(
        [question_clip, cta_clip],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(TOTAL_DURATION).with_fps(FPS)

    # --------------------------------------------------
    # AUDIO
    # --------------------------------------------------
    if music_path.exists():
        print(f"Adding background music from path: {music_path}")
        audio = AudioFileClip(str(music_path)).subclipped(0, TOTAL_DURATION)
        audio = audio.with_volume_scaled(0.35)
        final_video = final_video.with_audio(audio)
    else:
        # Ensure an audio track exists to keep player volume control enabled
        duration = final_video.duration or TOTAL_DURATION
        fps_audio = 44100
        n_samples = int(duration * fps_audio)
        silence = np.zeros((n_samples, 2), dtype=np.float32)
        silent_audio = AudioArrayClip(silence, fps=fps_audio)
        final_video = final_video.with_audio(silent_audio)

    # --------------------------------------------------
    # EXPORT
    # --------------------------------------------------
    output_path.parent.mkdir(parents=True, exist_ok=True)
    final_video.write_videofile(
        str(output_path),
        codec="libx264",
        preset="ultrafast",
        audio_codec="aac",
        fps=FPS,
        threads=4
    )

    print(f"Video saved to {output_path}")
