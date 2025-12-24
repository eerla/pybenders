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

VIDEO_W, VIDEO_H = 1080, 1920
FPS = 30
SAFE_WIDTH = 960
QUESTION_DURATION = 1
CTA_DURATION = 1
TOTAL_DURATION = QUESTION_DURATION + CTA_DURATION

RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
RUN_DATE = datetime.now().strftime("%Y%m%d")

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


# def generate_day1_reel(
#     welcome_img: Path,
#     question_img: Path,
#     cta_img: Path | None = None,
#     music_path: Path | None = None,
# ):
def generate_day1_reel(
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
        music_path = Path("assets/music/chill_loop.mp3")
    # --------------------------------------------------
    # Output Path (timestamped)
    # --------------------------------------------------
    out_dir = Path(f"output/reels/day1/{RUN_DATE}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{RUN_TIMESTAMP}_day1_reel.mp4"

    # --------------------------------------------------
    # Durations
    # --------------------------------------------------
    WELCOME_DUR = 2.0
    QUESTION_DUR = 7.0
    CTA_DUR = 4.0
    FADE_DUR = 0.6

    # --------------------------------------------------
    # Welcome Clip
    # --------------------------------------------------
    welcome_clip = (
        ImageClip(str(welcome_img))
        .resized(height=VIDEO_H)
        .with_duration(WELCOME_DUR)
        .with_fps(FPS)
        .with_effects([vfx.Resize(1.02), vfx.FadeOut(FADE_DUR)])
    )

    # --------------------------------------------------
    # Question Clip
    # --------------------------------------------------
    question_clip = (
        ImageClip(str(question_img))
        .resized(height=VIDEO_H)
        .with_duration(QUESTION_DUR)
        .with_fps(FPS)
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
        .resized(height=VIDEO_H)
        .with_duration(CTA_DUR)
        .with_fps(FPS)
        .with_start(WELCOME_DUR + QUESTION_DUR - (FADE_DUR * 2))
        .with_effects([vfx.FadeIn(FADE_DUR)])
    )


    # --------------------------------------------------
    # Composite
    # --------------------------------------------------
    final_video = CompositeVideoClip(
        [welcome_clip, question_clip, cta_clip],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(
        WELCOME_DUR + QUESTION_DUR + CTA_DUR
    ).with_fps(FPS)

    # --------------------------------------------------
    # Audio (optional)
    # --------------------------------------------------
    if music_path and music_path.exists():
        audio = (
            AudioFileClip(str(music_path))
            .subclipped(0, final_video.duration)
            .with_volume_scaled(0.25)
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
        fps=FPS,
        preset="ultrafast",
        threads=4
    )

    print(f"✅ Day 1 reel generated at: {out_path}")


def generate_day2_reel(
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
        music_path = Path("assets/music/chill_loop.mp3")

    # --------------------------------------------------
    # Output Path (same RUN_TIMESTAMP as Day 1)
    # --------------------------------------------------
    out_dir = Path(f"output/reels/day2/{RUN_DATE}")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{RUN_TIMESTAMP}_day2_reel.mp4"

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
        .resized(height=VIDEO_H)
        .with_duration(QUESTION_DUR)
        .with_fps(FPS)
        .with_effects([vfx.Resize(1.02), vfx.FadeOut(FADE_DUR)])
    )

    # --------------------------------------------------
    # Answer Reveal Clip (main highlight)
    # --------------------------------------------------
    answer_clip = (
        ImageClip(str(answer_img))
        .resized(height=VIDEO_H)
        .with_duration(ANSWER_DUR)
        .with_fps(FPS)
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
        .resized(height=VIDEO_H)
        .with_duration(CTA_DUR)
        .with_fps(FPS)
        .with_start(QUESTION_DUR + ANSWER_DUR - (FADE_DUR * 2))
        .with_effects([vfx.Resize(1.02), vfx.FadeIn(FADE_DUR)])
    )

    # --------------------------------------------------
    # Composite
    # --------------------------------------------------
    final_video = CompositeVideoClip(
        [question_clip, answer_clip, cta_clip],
        size=(VIDEO_W, VIDEO_H)
    ).with_duration(
        QUESTION_DUR + ANSWER_DUR + CTA_DUR
    ).with_fps(FPS)

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
        fps=FPS,
        preset="ultrafast",
        threads=4
    )

    print(f"✅ Day 2 reel generated at: {out_path}")
