# pybenders/generator/schema.py
from pydantic import BaseModel
from typing import List

class Question(BaseModel):
    title: str
    code: str
    question: str
    options: List[str]
    correct: str
    explanation: str
