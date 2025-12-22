from pathlib import Path
from pybender.render.video import create_question_reel

def main():
    create_question_reel(
        question_image=Path("output/images/question_1.png"),
        music_path=Path("pybenders/assets/music/chill_loop.mp3"),
        output_path=Path("output/reels/question_1.mp4")
    )

    print("Reel created successfully")

if __name__ == "__main__":
    main()
