

from typing import Dict

def validate_code_output(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long (max 8 words)"
    assert q["code"].count("\n") <= 12, "Code too long (max 12 lines)"
    assert len(q["question"]) <= 200, "Question too long (max 200 chars)"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long (max 60 chars)"
    assert len(q["explanation"]) <= 300, "Explanation too long (max 300 chars)"


def validate_query_output(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long (max 8 words)"
    assert q["code"].count("\n") <= 12, "Code too long (max 12 lines)"
    assert "WITH" in q["code"] and "VALUES" in q["code"], "Code must embed sample data via CTE VALUES"
    assert len(q["question"]) <= 110, "Question too long (max 110 chars)"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long (max 60 chars)"
    assert len(q["explanation"]) <= 300, "Explanation too long (max 300 chars)"


def validate_pattern_match(q: dict):
    assert len(q["title"].split()) <= 6, "Title too long (max 6 words)"
    assert len(q["code"]) <= 120, "Code too long (max 120 chars)"
    assert len(q["question"]) <= 200, "Question too long (max 200 chars)"
    assert all(len(opt) <= 60 for opt in q["options"]), "Option too long (max 60 chars)"
    assert len(q["explanation"]) <= 300, "Explanation too long (max 300 chars)"

def validate_scenario(q: dict):
    assert len(q["title"].split()) <= 8, "Title too long (max 8 words)"
    assert len(q["scenario"]) <= 350, "Scenario too long (max 350 chars)"
    assert len(q["scenario"]) >= 30, "Scenario too short (min 30 chars)"
    assert len(q["question"]) <= 150, "Question too long (max 150 chars)"
    assert all(len(opt) <= 75 for opt in q["options"]), "Option too long (max 75 chars)"
    assert len(q["explanation"]) <= 400, "Explanation too long (max 400 chars)"

def validate_command_output(q: dict):
    assert len(q["title"].split()) <= 6, "Title too long (max 6 words)"
    assert q["code"].count("\n") <= 6, "Code too long (max 6 lines)"
    assert len(q["question"]) <= 120, "Question too long (max 120 chars)"
    assert all(len(opt) <= 55 for opt in q["options"]), "Option too long (max 55 chars)"
    assert len(q["explanation"]) <= 300, "Explanation too long (max 300 chars)"

def validate_qa(q: dict):
    assert len(q["title"].split()) <= 7, "Title too long (max 7 words)"
    assert len(q["scenario"]) <= 350, "Scenario too long (max 350 chars)"
    assert len(q["scenario"]) >= 30, "Scenario too short (min 30 chars)"
    assert q["code"].strip() == "" or len(q["code"]) <= 50, "Code too long (max 50 chars)"
    assert len(q["question"]) <= 150, "Question too long (max 150 chars)"
    assert all(len(opt) <= 75 for opt in q["options"]), "Option too long (max 75 chars)"
    assert len(q["explanation"]) <= 400, "Explanation too long (max 400 chars)"

def validate_mind_bender(q: dict):
    assert len(q["title"].split()) <= 6, "Title too long (max 6 words)"
    assert len(q["puzzle"]) <= 100, "Puzzle too long (max 100 chars)"
    
    # Validate combined puzzle + visual_elements (as rendered together)
    puzzle_combined = q["puzzle"]
    if q.get("visual_elements"):
        puzzle_combined += f"\n{q['visual_elements']}"
    assert len(puzzle_combined) <= 230, "Combined puzzle + visual_elements too long (max 230 chars)"
    
    assert len(q["question"]) <= 100, "Question too long (max 100 chars)"
    assert len(q["options"]) == 4, "There must be exactly 4 options"
    assert all(len(opt) <= 40 for opt in q["options"]), "Option too long (max 40 chars)"
    assert len(q["explanation"]) <= 300, "Explanation too long (max 300 chars)"
    if q.get("fun_fact"):
        assert len(q["fun_fact"]) <= 200, "Fun fact too long (max 200 chars)"


def validate_psychology_card(q: dict):
    allowed_categories = {
        "cognitive_bias",
        "social_psychology",
        "behavioral_economics",
        "mental_health",
        "decision_making",
        "perception",
        "memory",
        "emotions",
        "relationships",
        "motivation",
    }

    assert len(q["title"].split()) <= 6, "Title too long (max 6 words)"
    assert q.get("category") in allowed_categories, "Invalid category"
    assert len(q["statement"]) <= 150, "Statement too long (max 150 chars)"
    assert len(q["explanation"]) <= 250, "Explanation too long (max 250 chars)"
    assert len(q["real_example"]) <= 200, "Real example too long (max 200 chars)"
    assert len(q["application"]) <= 150, "Application too long (max 150 chars)"
    if q.get("application"):
        assert q["application"].lower().startswith("try this:"), "Application must start with 'Try this:'"
    if q.get("source"):
        assert len(q["source"]) <= 50, "Source too long (max 50 chars)"


def validate_finance_card(q: dict):
    allowed_categories = {
        "investing",
        "budgeting",
        "taxes",
        "personal_finance",
        "markets",
        "risk_management",
        "retirement",
        "fintech",
    }

    assert len(q["title"].split()) <= 6, "Title too long (max 6 words)"
    assert q.get("category") in allowed_categories, "Invalid category"
    assert len(q["insight"]) <= 140, "Insight too long (max 140 chars)"
    assert len(q["explanation"]) <= 220, "Explanation too long (max 220 chars)"
    assert len(q["example"]) <= 180, "Example too long (max 180 chars)"
    assert len(q["action"]) <= 130, "Action too long (max 130 chars)"
    if q.get("action"):
        assert q["action"].lower().startswith("try this:"), "Action must start with 'Try this:'"
    if q.get("source"):
        assert len(q["source"]) <= 50, "Source too long (max 50 chars)"


VALIDATORS: Dict[str, callable] = {
    "code_output": validate_code_output,
    "query_output": validate_query_output,
    "pattern_match": validate_pattern_match,
    "scenario": validate_scenario,
    "command_output": validate_command_output,
    "qa": validate_qa,
    "mind_bender": validate_mind_bender,
    "wisdom_card": validate_psychology_card,
    "finance_card": validate_finance_card,
}


