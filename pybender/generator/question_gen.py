# pybenders/generator/question_gen.py
import json
import random
from openai import OpenAI
from datetime import datetime
from pybender.config.settings import OPENAI_API_KEY, MODEL
from pybender.generator.schema import Question
from pybender.generator.prompt_loader import load_prompt
import os

client = OpenAI(api_key=OPENAI_API_KEY)
PYTHON_TOPICS = [
    "Python internals and memory model",
    "List comprehensions and generators",
    "Variable scope and closures",
    "Mutability and immutability",
    "Decorators",
    "Async and await",
    "Threading and GIL",
    "Standard library gotchas",
    "Object-oriented Python internals",
    "Python truthiness and comparisons"
]

RUN_DATE = datetime.now().strftime("%Y%m%d")
RUN_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

def generate_questions(n: int) -> list[Question]:
    topic = random.choice(PYTHON_TOPICS)
    prompt_template = load_prompt("python_mcq.txt")

    prompt = prompt_template.replace("{{topic}}", topic)\
                             .replace("{{n}}", str(n))
    # print(prompt)
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": "You generate only valid JSON."},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    # print("LLM Response:")
    # print(raw)
    try:
        data = json.loads(raw)
        output_dir = f"output/data/questions/{RUN_DATE}"
        os.makedirs(output_dir, exist_ok=True)
        output_file = f"{output_dir}/questions_{RUN_TIMESTAMP}.json"
        with open(output_file, "w") as f:
            json.dump(data, f, indent=4)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    return [Question(**q) for q in data]
