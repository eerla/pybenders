# pybenders/generator/question_gen.py
import json
import logging
import random
from datetime import datetime
from openai import OpenAI

from pybender.config.logging_config import setup_logging
from pybender.config.settings import OPENAI_API_KEY, MODEL
from pybender.generator.schema import Question, MindBenderQuestion, PsychologyCard
from pybender.generator.content_registry import CONTENT_REGISTRY
from pybender.prompts.templates import PROMPT_TEMPLATES
from pybender.validation.validate_questions import validate_questions


logger = logging.getLogger(__name__)


def _ensure_logging_configured() -> None:
    if not logging.getLogger().handlers:
        setup_logging()


class ValidationError(Exception):
    pass

class QuestionGenerator:

    def __init__(self):
        _ensure_logging_configured()
        self.client = OpenAI(api_key=OPENAI_API_KEY)
        self.run_date = datetime.now().strftime("%Y%m%d")
        self.run_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.model = "gpt-4o-mini"
        self.MAX_RETRIES = 2

    def get_llm_response(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You generate only valid JSON."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content

    def generate_questions(self, n: int, subject: str = "python") -> tuple[list[Question], str]:
        
        spec = CONTENT_REGISTRY[subject]
        topic = random.choice(spec.topics)
        content_type = spec.content_type
        prompt_template = PROMPT_TEMPLATES[content_type]

        prompt = (
            prompt_template
            .replace("{{subject}}", subject)
            .replace("{{topic}}", topic)
            .replace("{{n}}", str(n))
        )

        try:
            logger.info("🧠 Generating %s questions via LLM for %s on topic: %s", n, subject, topic)
            raw = self.get_llm_response(prompt)
            logger.info("💬 Raw LLM response:\n%s", raw)
            if not raw or not raw.strip():
                raise ValueError(f"LLM returned empty response for subject {subject} on topic {topic}")
            
            # Strip markdown code blocks if present (e.g., ```json ... ```)
            raw = raw.strip()
            if raw.startswith("```"):
                # Remove opening code block marker (```json or ```)
                raw = raw.split("\n", 1)[1] if "\n" in raw else raw[3:]
            if raw.endswith("```"):
                # Remove closing code block marker
                raw = raw.rsplit("\n", 1)[0] if "\n" in raw else raw[:-3]
            raw = raw.strip()
            
            data = json.loads(raw)
        except json.JSONDecodeError:
            raise ValueError(f"LLM returned invalid JSON for subject {subject} on topic {topic} \
                                \n raw response: {raw}")

        valid, failed = validate_questions(data, content_type)

        attempt = 0
        while failed and attempt < self.MAX_RETRIES:
            attempt += 1
            logger.info("🔁 Retry %s: regenerating %s invalid questions", attempt, len(failed))

            regenerated = self.regenerate_failed_questions(
                failed,
                subject=subject,
                content_type=content_type
            )

            valid_retry, failed = validate_questions(regenerated, content_type)
            valid.extend(valid_retry)

        if failed:
            logger.warning("⚠️ Dropping %s questions after %s retries", len(failed), self.MAX_RETRIES)

        # Return subject-specific question models
        if subject == "mind_benders" or content_type == "puzzle":
            return [MindBenderQuestion(**q) for q in valid], topic, content_type
        if content_type == "wisdom_card":
            return [PsychologyCard(**q) for q in valid], topic, content_type

        return [Question(**q) for q in valid], topic, content_type

    def regenerate_failed_questions(
            self,
            failed: list[dict],
            subject: str,
            content_type: str
        ) -> list[dict]:

        constraint_block = "\n".join(
            f"- {q.get('_validation_error', 'Unknown error')}"
            for q in failed
        )

        retry_prompt = f"""
        The following {subject} questions failed formatting validation.

        Constraints violated:
        {constraint_block}

        Fix ONLY formatting issues.
        Do NOT change the core idea.
        Strictly obey all constraints.

        Return ONLY valid JSON (array of questions).

        Questions:
        {json.dumps(failed, indent=2)}
        """

        return json.loads(self.get_llm_response(retry_prompt))
