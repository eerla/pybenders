

from typing import Dict

def validate_code_output(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long"
    assert q["code"].count("\n") <= 8, "Code too long"
    assert len(q["question"].split(".")) <= 2, "Question too verbose"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long"
    assert len(q["explanation"]) <= 180, "Explanation too long"


def validate_query_output(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long"
    assert q["code"].count("\n") <= 8, "Code too long (max 8 lines)"
    assert "WITH" in q["code"] and "VALUES" in q["code"], "Code must embed sample data via CTE VALUES"
    assert len(q["question"]) <= 110, "Question too long"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long"
    assert len(q["explanation"]) <= 170, "Explanation too long"


def validate_pattern_match(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long"
    assert q["code"].count("\n") <= 8, "Code too long"
    assert len(q["question"].split(".")) <= 2, "Question too verbose"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long"
    assert len(q["explanation"]) <= 180, "Explanation too long"

def validate_scenario(q: dict):
    assert len(q["title"].split()) <= 8
    assert len(q["scenario"]) <= 350, "Scenario too long (max 350)"
    assert len(q["scenario"]) >= 30, "Scenario too short (min 30)"
    assert len(q["question"]) <= 150, "Question too long (max 150)"
    assert all(len(opt) <= 75 for opt in q["options"]), "Option too long (max 75)"
    assert len(q["explanation"]) <= 400, "Explanation too long (max 400)"

def validate_command_output(q: dict):
    assert len(q["title"].split()) <= 8
    assert q["code"].count("\n") <= 4     # short commands
    assert len(q["question"]) <= 120
    assert all(len(opt) <= 60 for opt in q["options"])
    assert len(q["explanation"]) <= 160

def validate_qa(q: dict):
    assert len(q["title"].split()) <= 8
    assert len(q["scenario"]) <= 350, "Scenario too long (max 350)"
    assert len(q["scenario"]) >= 30, "Scenario too short (min 30)"
    assert q["code"].strip() == "" or len(q["code"]) <= 50, "Code too long (max 50)"
    assert len(q["question"]) <= 150, "Question too long (max 150)"
    assert all(len(opt) <= 75 for opt in q["options"]), "Option too long (max 75)"
    assert len(q["explanation"]) <= 400, "Explanation too long (max 400)"

VALIDATORS: Dict[str, callable] = {
    "code_output": validate_code_output,
    "query_output": validate_query_output,
    "pattern_match": validate_pattern_match,
    "scenario": validate_scenario,
    "command_output": validate_command_output,
    "qa": validate_qa,
}


