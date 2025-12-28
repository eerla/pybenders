

from typing import Dict

def validate_code_output(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long"
    assert q["code"].count("\n") <= 8, "Code too long"
    assert len(q["question"].split(".")) <= 2, "Question too verbose"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long"
    assert len(q["explanation"]) <= 180, "Explanation too long"


def validate_query_output(q: dict):
    assert q["query"].count("\n") <= 6
    assert len(q["question"]) <= 120


def validate_pattern_match(q: dict):
    assert len(q["regex"]) <= 40
    assert len(q["input"]) <= 80

def validate_scenario(q: dict):
    assert len(q["title"].split()) <= 8
    assert len(q["question"]) <= 220
    assert all(len(opt) <= 80 for opt in q["options"])
    assert len(q["explanation"]) <= 200
    assert len(q["scenario"]) >= 30

def validate_command_output(q: dict):
    assert len(q["title"].split()) <= 6
    assert q["code"].count("\n") <= 4     # short commands
    assert len(q["question"]) <= 120
    assert all(len(opt) <= 60 for opt in q["options"])
    assert len(q["explanation"]) <= 160

def validate_qa(q: dict):
    assert len(q["title"].split()) <= 7
    assert q["code"].strip() == "" or len(q["code"]) <= 40
    assert len(q["question"]) <= 180
    assert all(len(opt) <= 70 for opt in q["options"])
    assert len(q["explanation"]) <= 200
    assert len(q["scenario"]) >= 30

VALIDATORS: Dict[str, callable] = {
    "code_output": validate_code_output,
    "query_output": validate_query_output,
    "pattern_match": validate_pattern_match,
    "scenario": validate_scenario,
    "command_output": validate_command_output,
    "qa": validate_qa,
}


