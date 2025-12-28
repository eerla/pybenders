# pybenders/generator/schema.py
from pydantic import BaseModel, Field
from typing import List, Optional

class Question(BaseModel):
    question_id: Optional[str] = Field(default=None)
    title: str
    code: str
    scenario: Optional[str] = Field(default='')
    question: str
    options: List[str]
    correct: str
    explanation: str
