#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

from users.ai_question_generator import generate_difficulty_questions

# Testing AI question generating with programming
questions = generate_difficulty_questions('programming')

print("=== GENERATED QUESTIONS ===")
for i, q in enumerate(questions, 1):
    print(f"\nQuestion {i}: {q.question}")
    for j, option in enumerate(q.answer):
        print(f"  {chr(65+j)}. {option}")  # A, B, C, D
    print(f"  Correct: {chr(65+q.correct_answer)} | Level: {q.difficulty_level} | Points: {q.points}")

print(f"\nTotal Questions: {len(questions)}")



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learningPlatform.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
