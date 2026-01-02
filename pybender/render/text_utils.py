"""Shared text and code wrapping helpers for renderers."""
import re
from typing import List


def slugify(text: str) -> str:
    return text.lower().replace(" ", "_")


def wrap_code_line(draw, line: str, font, max_width: int) -> List[str]:
    stripped = line.lstrip(" ")
    indent = line[: len(line) - len(stripped)]

    if not stripped:
        return [line]

    words = stripped.split(" ")
    lines: List[str] = []
    current = ""

    for word in words:
        test = (current + " " + word).strip()
        width = draw.textlength(indent + test, font=font)

        if width <= max_width:
            current = test
        else:
            if current:
                lines.append(indent + current)
            current = word

    if current:
        lines.append(indent + current)

    return lines


def wrap_text(draw, text: str, font, max_width: int) -> List[str]:
    """Wrap text so each line fits within max_width."""
    if not text:
        return [""]
    words = text.split(" ")
    lines: List[str] = []
    current = ""

    for word in words:
        test = current + (" " if current else "") + word
        if draw.textlength(test, font=font) <= max_width:
            current = test
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def wrap_text_with_prefix(draw, text: str, font, max_width: int, prefix_width: int) -> List[str]:
    """Wrap text where first line has reduced width due to prefix."""
    if not text:
        return [""]

    words = text.split(" ")
    lines: List[str] = []
    current = ""

    line_limit = max_width - (prefix_width or 0)

    for word in words:
        test = current + (" " if current else "") + word
        if draw.textlength(test, font=font) <= line_limit:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
            line_limit = max_width

    if current:
        lines.append(current)

    return lines


def normalize_code(code: str) -> List[str]:
    """Normalize code: handle literal \n, tabs to spaces, strip trailing whitespace."""
    if not code:
        return []

    code = code.replace("\\n", "\n")
    lines: List[str] = []
    for line in code.split("\n"):
        line = line.replace("\t", " " * 4)
        lines.append(line.rstrip())
    return lines
