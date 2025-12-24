# tests/test_question_gen.py
from pybender.generator.question_gen import generate_questions

qs = generate_questions(2)

for q in qs:
    print(q.title)
    print(q.code)
    print(q.options)
    print("Answer:", q.correct)
    print("Explanation:", q.explanation)
