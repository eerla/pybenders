from pathlib import Path
from pybender.generator.question_gen import generate_questions, Question
from pybender.render.image import render_welcome_image
import json

def main():
   
    render_welcome_image()

    print("CTA Image rendered successfully")

if __name__ == "__main__":
    main()
