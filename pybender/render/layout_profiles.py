# pybender/render/layout_profiles.py
from dataclasses import dataclass

@dataclass(frozen=True)
class LayoutProfile:
    name: str
    has_code: bool
    has_options: bool
    has_explanation: bool
    code_style: str | None  # editor | terminal | none


CODE_OUTPUT = LayoutProfile(
    name="code_output",
    has_code=True,
    has_options=True,
    has_explanation=True,
    code_style="editor",
)

QA = LayoutProfile(
    name="qa",
    has_code=False,
    has_options=True,
    has_explanation=True,
    code_style=None,
)

SCENARIO = LayoutProfile(
    name="scenario",
    has_code=False,
    has_options=True,
    has_explanation=True,
    code_style=None,
)

COMMAND_OUTPUT = LayoutProfile(
    name="command_output",
    has_code=True,
    has_options=True,
    has_explanation=True,
    code_style="terminal",
)

PATTERN_MATCH = LayoutProfile(
    name="pattern_match",
    has_code=True,
    has_options=True,
    has_explanation=True,
    code_style="regex_highlight",
)

QUERY_OUTPUT = LayoutProfile(
    name="query_output",
    has_code=True,
    has_options=True,
    has_explanation=True,
    code_style="query_result",
)

LAYOUT_PROFILES = {
    "code_output": CODE_OUTPUT,
    "qa": QA,
    "scenario": SCENARIO,
    "command_output": COMMAND_OUTPUT,
    "pattern_match": PATTERN_MATCH,
    "query_output": QUERY_OUTPUT,
}
