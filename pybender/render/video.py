from moviepy import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip,
    AudioArrayClip,
    TextClip,
    vfx,
    concatenate_videoclips,
    ColorClip,
)
from pathlib import Path
import numpy as np

VIDEO_W, VIDEO_H = 1080, 1920
FPS = 30
SAFE_WIDTH = 960


def create_question_reel(
    question_image: Path,
    music_path: Path,
    output_path: Path
):
    # --------------------------------------------------
    # QUESTION CLIP (0–5s) — static, fit-to-screen (contain)
    base_img = ImageClip(str(question_image))
    scale = min(VIDEO_W / base_img.w, VIDEO_H / base_img.h)
    fg_q = (
        base_img
        .resized(scale)
        .with_duration(5)
        .with_position("center")
    )

    question_clip = CompositeVideoClip(
        [fg_q],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(5)

    # --------------------------------------------------
    # CTA CLIP (15–25s)
    # --------------------------------------------------

    # CTA Background (solid color, no image overlay)
    bg_cta = ColorClip(size=(VIDEO_W, VIDEO_H), color=(9, 12, 24)).with_duration(5)

    # CTA Card (semi-transparent panel)
    card_overlay = (
        TextClip(
            text=" ",
            font_size=10,
            color="white",
            size=(920, 720),
            method="caption",
            bg_color="#0B1220"
        )
        .with_opacity(0.85)
        .with_duration(5)
        .with_position("center")
    )

    # CTA Text – Title
    cta_title = (
        TextClip(
            text="Drop Your Answer Below in Comments!",
            font_size=72,
            font=None,
            color="#4CC9F0",
            method="caption",
            size=(820, None),
            text_align="center",
            interline=8,
            margin=(10, 10)
        )
        .with_duration(5)
        .with_position(("center", VIDEO_H // 2 - 240))
    )

    # CTA Text – Body
    cta_body = (
        TextClip(
            text="A / B / C / D\n\nAnswer revealed in 24 hours",
            font_size=50,
            font=None,
            color="white",
            method="caption",
            size=(820, None),
            text_align="center",
            interline=10,
            margin=(10, 16)
        )
        .with_duration(5)
        .with_position(("center", VIDEO_H // 2 - 20))
    )

    # CTA Text – Follow Hook
    cta_follow = (
        TextClip(
            text="Follow for more Python Tricky Questions",
            font_size=44,
            font=None,
            color="#A0AEC0",
            method="caption",
            size=(820, None),
            text_align="center",
            interline=8,
            margin=(10, 10)
        )
        .with_duration(5)
        .with_position(("center", VIDEO_H // 2 + 220))
    )

    cta_clip = CompositeVideoClip(
        [
            bg_cta,
            card_overlay,
            cta_title,
            cta_body,
            cta_follow
        ],
        size=(VIDEO_W, VIDEO_H)
    ).with_start(5)

    # --------------------------------------------------
    # FINAL COMPOSITION
    # --------------------------------------------------

    final_video = CompositeVideoClip(
        [question_clip, cta_clip],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(10).with_fps(FPS)

    # --------------------------------------------------
    # AUDIO
    # --------------------------------------------------

    if music_path.exists():
        print(f"Adding background music from path: {music_path}")
        audio = AudioFileClip(str(music_path)).subclipped(0, 10)
        audio = audio.with_volume_scaled(0.35)
        final_video = final_video.with_audio(audio)
    else:
        # Ensure an audio track exists to keep player volume control enabled
        duration = final_video.duration or 10
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
        preset="ultrafast",  # veryfast, default = medium
        audio_codec="aac",
        fps=FPS,
        threads=4
    )

    print(f"Video saved to {output_path}")
