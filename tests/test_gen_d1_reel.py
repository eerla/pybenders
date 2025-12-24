from pathlib import Path
from pybender.render.video import generate_day1_reel
from datetime import datetime
import os
import random

def main():
    questions_images = os.listdir("output/images/questions")
    qi = random.choice(questions_images)
    qi_path = Path("output/images/questions") / qi

    generate_day1_reel(question_img=qi_path)

    print("Reel created successfully")

if __name__ == "__main__":
    main()

