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


class MindBenderQuestion(BaseModel): # mind_bender profile
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
    

class PsychologyCategory(str, Enum):
    COGNITIVE_BIAS = "cognitive_bias"
    SOCIAL_PSYCHOLOGY = "social_psychology"
    BEHAVIORAL_ECONOMICS = "behavioral_economics"
    MENTAL_HEALTH = "mental_health"
    DECISION_MAKING = "decision_making"
    PERCEPTION = "perception"
    MEMORY = "memory"
    EMOTIONS = "emotions"
    RELATIONSHIPS = "relationships"
    MOTIVATION = "motivation"

class PsychologyCard(BaseModel): # wisdom_card profile
    """Schema for psychology wisdom cards."""
    question_id: Optional[str] = None
    title: str  # "The Dunning-Kruger Effect" (max 6 words)
    category: PsychologyCategory
    statement: str  # Main fact (150 chars - short, punchy)
    explanation: str  # Why it matters (250 chars)
    real_example: str  # Everyday scenario (200 chars)
    application: str  # "Try this: ..." actionable tip (150 chars)
    source: Optional[str] = ""  # "Study: MIT 2023" or similar


class FinanceCategory(str, Enum):
    INVESTING = "investing"
    BUDGETING = "budgeting"
    TAXES = "taxes"
    PERSONAL_FINANCE = "personal_finance"
    MARKETS = "markets"
    RISK_MANAGEMENT = "risk_management"
    RETIREMENT = "retirement"
    FINTECH = "fintech"


class FinanceCard(BaseModel):
    """Schema for finance insight cards."""
    question_id: Optional[str] = None
    title: str  # "Index Funds Beat Most Funds" (max 6 words)
    category: FinanceCategory
    insight: str  # Main point (140 chars)
    explanation: str  # Why it matters (220 chars)
    example: str  # Concrete scenario (180 chars)
    action: str  # "Try this: ..." actionable tip (130 chars)
    source: Optional[str] = ""  # Optional citation (50 chars)