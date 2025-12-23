from pathlib import Path
from pybender.generator.question_gen import generate_questions, Question
from pybender.render.image import render_single_post_image
import json

def main():
    # questions = generate_questions("python internals", 1)
    with open("output/questions.json", "r") as f:
        questions_data = json.load(f)
        questions = [Question(**q) for q in questions_data]
    output_dir = Path("output/images/answers")
    output_dir.mkdir(parents=True, exist_ok=True)

    for question in questions:
        # print(question)
        render_single_post_image(
            question,
        )

    print("Image rendered successfully")

if __name__ == "__main__":
    main()
