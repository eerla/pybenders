# pybenders/generator/question_gen.py
import json
import random
from datetime import datetime
from openai import OpenAI

from pybender.config.settings import OPENAI_API_KEY, MODEL
from pybender.generator.schema import Question
from pybender.generator.prompt_loader import load_prompt

class ValidationError(Exception):
    pass

class QuestionGenerator:
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

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.run_date = datetime.now().strftime("%Y%m%d")
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.model = "gpt-4o-mini"
        self.MAX_RETRIES = 2

    @staticmethod
    def validate_question(q: dict) -> None:
        if len(q["title"].split()) > 8:
            raise ValidationError("Title too long")

        if q["code"].count("\n") >= 8:
            raise ValidationError("Code too long")

        # # crude but effective single-sentence check
        # if q["question"].count(".") != 2:
        #     raise ValidationError("Question must be exactly one sentence")

        if any(len(opt) > 60 for opt in q["options"]):
            raise ValidationError("Option too long")

        if len(q["explanation"]) > 180:
            raise ValidationError("Explanation too long")

    def generate_questions(self, n: int) -> tuple[list[Question], str]:
        topic = random.choice(self.PYTHON_TOPICS)
        prompt_template = load_prompt("python_mcq.txt")

        prompt = prompt_template.replace("{{topic}}", topic)\
                                 .replace("{{n}}", str(n))

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )

        raw = response.choices[0].message.content
        validated_questions = []
        try:
            data = json.loads(raw)
            for q in data:
                q = self.validate_with_retry(q)
                validated_questions.append(Question(**q))

        except json.JSONDecodeError:
            raise ValueError("LLM returned invalid JSON")

        return validated_questions, topic

    def regenerate_question(self, original_q: dict, error: str) -> dict:
        prompt = f"""
            The following Python MCQ violates formatting rules.

            Error: {error}

            Original question (JSON):
            {json.dumps(original_q, indent=2)}

            Fix ONLY the formatting issues.
            Do NOT change the core idea.
            Follow all original constraints strictly.
            Return ONLY valid JSON for a single question.
        """

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You output only valid JSON."},
                {"role": "user", "content": prompt}
            ],
        )

        return json.loads(response.choices[0].message.content)

    def validate_with_retry(self, q: dict) -> dict:
        attempt = 0
        while attempt <= self.MAX_RETRIES:
            try:
                self.validate_question(q)
                return q
            except ValidationError as e:
                if attempt == self.MAX_RETRIES:
                    raise RuntimeError(
                        f"Question failed validation after retries: {e}"
                    )
                q = self.regenerate_question(q, str(e))
                attempt += 1
