## DEPRECATED FILE. USE prompt/template.py INSTEAD.
PROMPT_MAP = {
    "code_output": "python_mcq.txt",
    "query_output": "sql_query.txt",
    "pattern_match": "regex.txt",
    "scenario": "system_design.txt",
    "command_output": "linux.txt",
    "qa": "devops.txt",
}


# subject
#   ↓
# CONTENT_REGISTRY
#   ↓
# content_type
#   ↓
# PROMPT_TEMPLATES[content_type]
#   ↓
# LLM
#   ↓
# validator[content_type]
#   ↓
# renderer[content_type]
