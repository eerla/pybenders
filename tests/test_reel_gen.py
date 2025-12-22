from pathlib import Path
from pybender.render.video import create_question_reel
from datetime import datetime

def main():
    create_question_reel(
        question_image=Path("output/images/question_1.png"),
        music_path=Path("pybender/assets/music/chill_loop.mp3"),
        output_path=Path(f"output/reels/question_1_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
    )

    print("Reel created successfully")

if __name__ == "__main__":
    main()
