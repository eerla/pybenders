# from pathlib import Path
# from pybender.render.video import create_question_reel
# from datetime import datetime
# import os
# import random

# def main():
#     # questions_images = os.listdir("output/images")
#     # qi = random.choice(questions_images)
#     # qi_path = Path("output/images") / qi

#     # create_question_reel(
#     #     question_image=qi_path,
#     #     music_path=Path("pybender/assets/music/chill_loop.mp3"),
#     #     output_path=Path(f"output/reels/{qi}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
#     # )

#     # print("Reel created successfully")

# if __name__ == "__main__":
#     main()


from pathlib import Path
from pybender.render.video import generate_day1_reel
from pybender.render.video import generate_day2_reel
from datetime import datetime
import os
import random
from concurrent.futures import ThreadPoolExecutor

def main():
    questions_images = os.listdir("output/images/questions")
    qi = random.choice(questions_images)
    qi_path = Path("output/images/questions") / qi
    ai_path = Path("output/images/answers") / qi
    
    with ThreadPoolExecutor(max_workers=2) as executor:
        executor.submit(generate_day1_reel, question_img=qi_path)
        executor.submit(generate_day2_reel, question_img=qi_path, answer_img=ai_path)

    print("Reel created successfully")

if __name__ == "__main__":
    main()

