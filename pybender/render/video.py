from moviepy import (
    ImageClip,
    CompositeVideoClip,
    AudioFileClip,
    TextClip,
    vfx,
    concatenate_videoclips
)
from pathlib import Path

VIDEO_W, VIDEO_H = 1080, 1920
FPS = 30
SAFE_WIDTH = 960


def create_question_reel(
    question_image: Path,
    music_path: Path,
    output_path: Path
):
    # --------------------------------------------------
    # QUESTION CLIP (0–20s)
    # --------------------------------------------------

    fg_start = (
        ImageClip(str(question_image))
        .resized(width=SAFE_WIDTH)
        .with_duration(10)
        .with_position("center")
        )

    fg_end = (
        ImageClip(str(question_image))
        .resized(width=int(SAFE_WIDTH * 1.03))
        .with_duration(10)
        .with_position("center")
    )

    fg_q = concatenate_videoclips(
        [fg_start, fg_end],
        method="compose"
    ).with_duration(20)

    bg_q = (
        ImageClip(str(question_image))
        .resized(height=VIDEO_H)
        .with_duration(20)
        .with_opacity(0.25)
    )

    question_clip = CompositeVideoClip(
        [bg_q, fg_q],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(20)

    # --------------------------------------------------
    # CTA CLIP (20–30s)
    # --------------------------------------------------

    # CTA Background (static, darkened)
    bg_cta = (
        ImageClip(str(question_image))
        .resized(height=VIDEO_H)
        .with_duration(10)
        .with_opacity(0.18)
    )

    # CTA Card (semi-transparent panel)
    card_bg = (
        ImageClip(str(question_image))
        .resized((800, 520))
        .with_opacity(0.0)  # invisible image holder
        .with_duration(10)
        .with_position("center")
    )

    card_overlay = (
        TextClip(
            text=" ",
            font_size=10,
            color="white",
            size=(800, 520),
            method="caption",
            bg_color="#0B1220"
        )
        .with_opacity(0.85)
        .with_duration(10)
        .with_position("center")
    )

    # CTA Text – Title
    cta_title = (
        TextClip(
            text="💬 Drop Your Answer Below",
            font_size=70,
            font=None,
            color="#4CC9F0",
            method="caption",
            size=(760, None),
            text_align="center"
        )
        .with_duration(10)
        .with_position(("center", VIDEO_H // 2 - 160))
    )

    # CTA Text – Body
    cta_body = (
        TextClip(
            text="A / B / C / D\n\n⏱ Answer revealed in 24 hours",
            font_size=48,
            font=None,
            color="white",
            method="caption",
            size=(760, None),
            text_align="center"
        )
        .with_duration(10)
        .with_position(("center", VIDEO_H // 2 - 20))
    )

    # CTA Text – Follow Hook
    cta_follow = (
        TextClip(
            text="➕ Follow for Python Internals & Tricky Questions",
            font_size=42,
            font=None,
            color="#A0AEC0",
            method="caption",
            size=(760, None),
            text_align="center"
        )
        .with_duration(10)
        .with_position(("center", VIDEO_H // 2 + 160))
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
    ).with_start(20)

    # --------------------------------------------------
    # FINAL COMPOSITION
    # --------------------------------------------------

    final_video = CompositeVideoClip(
        [question_clip, cta_clip],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(30).with_fps(FPS)

    # --------------------------------------------------
    # AUDIO
    # --------------------------------------------------

    if music_path.exists():
        audio = AudioFileClip(str(music_path)).subclipped(0, 30)
        audio = audio.with_volume_scaled(0.12)
        final_video = final_video.with_audio(audio)

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
