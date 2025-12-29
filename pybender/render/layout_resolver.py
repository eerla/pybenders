# pybender/render/layout_resolver.py
from pybender.render.layout_profiles import LAYOUT_PROFILES

CONTENT_TYPE_TO_PROFILE = {
    "code_output": "code_output",
    # "query_output": "query_output",
    # "pattern_match": "pattern_match",
    "query_output": "code_output",
    "pattern_match": "code_output",
    "command_output": "command_output",
    "qa": "qa",
    "scenario": "scenario",
}

def resolve_layout_profile(content_type: str):
    try:
        profile_key = CONTENT_TYPE_TO_PROFILE[content_type]
        return LAYOUT_PROFILES[profile_key]
    except KeyError:
        raise ValueError(f"Unknown content_type: {content_type}")
