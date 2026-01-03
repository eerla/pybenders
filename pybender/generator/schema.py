# pybenders/generator/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

from enum import Enum

class PuzzleCategory(str, Enum):
    NUMBER_PATTERN = "number_pattern"
    LOGIC = "logic"
    MATH_TRICK = "math_trick"
    WORD_PUZZLE = "word_puzzle"
    VISUAL = "visual"
    TRICK_QUESTION = "trick_question"
    AGE_PUZZLE = "age_puzzle"
    TIME_PUZZLE = "time_puzzle"
    PROBABILITY = "probability"
    APTITUDE = "aptitude"
    REASONING = "reasoning"

class AnswerOption(str, Enum):
    A = "A"
    B = "B"
    C = "C"
    D = "D"


class Question(BaseModel):
    question_id: Optional[str] = Field(default=None)
    title: str
    code: str
    scenario: Optional[str] = Field(default='')
    question: str
    options: List[str]
    correct: str
    explanation: str


class MindBenderQuestion(BaseModel):
    """Schema for brain teaser puzzle questions."""
    question_id: Optional[str] = None
    title: str  # "Number Pattern Challenge" (max 6 words)
    category: PuzzleCategory  # Type-safe enum
    puzzle: str  # Main puzzle text (e.g., "2, 6, 12, 20, ?")
    visual_elements: Optional[str] = ""  # "▲ ▲ ○" or emoji sequence
    hint: Optional[str] = ""  # Optional subtle hint
    question: str  # "What comes next?" (max 100 chars)
    options: List[str] = Field(..., min_items=4, max_items=4)  # Exactly 4 options
    correct: AnswerOption  # Type-safe: must be A, B, C, or D
    explanation: str  # Pattern explanation (max 300 chars)
    fun_fact: Optional[str] = ""  # Optional trivia (max 200 chars)
    