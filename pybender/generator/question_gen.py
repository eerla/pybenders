# pybenders/generator/question_gen.py
import json
from openai import OpenAI
from pybender.config.settings import OPENAI_API_KEY, MODEL
from pybender.generator.schema import Question
from pybender.generator.prompt_loader import load_prompt

client = OpenAI(api_key=OPENAI_API_KEY)
print(MODEL)
def generate_questions(topic: str, n: int) -> list[Question]:
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

    try:
        data = json.loads(raw)
        # add new step to append newly generated questions to a file
        try:
            with open("output/questions.json", "r") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
        
        existing_data.extend(data)
        
        with open("output/questions.json", "w") as f:
            json.dump(existing_data, f, indent=4)
    except json.JSONDecodeError:
        raise ValueError("LLM returned invalid JSON")

    return [Question(**q) for q in data]
