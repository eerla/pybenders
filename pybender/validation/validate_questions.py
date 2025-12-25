
from pybender.validation.validators import VALIDATORS

def validate_questions(questions: list[dict], content_type: str):
    validator = VALIDATORS.get(content_type)
    if not validator:
        return questions, []

    valid = []
    failed = []

    for q in questions:
        try:
            validator(q)
            valid.append(q)
        except AssertionError as e:
            q["_validation_error"] = str(e)
            failed.append(q)

    return valid, failed

