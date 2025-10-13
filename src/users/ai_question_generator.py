from groq import Groq
from pydantic import BaseModel
from typing import Literal, List
import json
from .models import DifficultyQuestions
from utils import config

from dotenv import load_dotenv

load_dotenv()

client = Groq()

class AssessmentQuestion(BaseModel):
    question: str
    answer: List[str]
    correct_answer: int
    difficulty_level: Literal['begginer', 'intermediate', 'advanced']
    points: int

class AssessmentQuestions(BaseModel):
    subject: str
    questions: List[AssessmentQuestion]


# PROBLEM: QUESTIONS ARE REGENERATED IN RETAKE ASSESSMENT AT EVERY PAGE RELOAD
def generate_difficulty_questions(subject, is_retake = False):
    
    existing_questions = DifficultyQuestions.objects.filter(subject = subject)
    
    if existing_questions.count() == 10 and not is_retake:
        pydantic_questions = []
        for q in existing_questions:
            pydantic_q = AssessmentQuestion(
                question = q.question_text,
                answer = q.answers,
                correct_answer = q.correct_answer,
                difficulty_level = q.difficulty_level,
                points = q.points
            )
            pydantic_questions.append(pydantic_q)
        
        return {'success': True, 'questions': pydantic_questions}
    
    else:
        existing_questions.delete()
    
        subject_prompt = {
            'programming': """ Generate 10 multiple choice questions to assess programming knowledge level. 
            Include questions covering: basic syntax, variables, functions, loops, and problem-solving. 
            Mix difficulty levels: 2 beginner (2 points each), 2 intermediate (3 points each), 1 advanced (4 points).
            Each question should have exactly 4 options.""",
            'music': """ Generate 10 multiple choice questions to assess musical theory and composition knowledge.
            Include questions covering: notes, scales, rhythm, harmony, and basic composition.
            Mix difficulty levels: 2 beginner (2 points each), 2 intermediate (3 points each), 1 advanced (4 points).
            Each question should have exactly 4 options.""",
            'art': """Generate 10 multiple choice questions to assess art history and crafting knowledge.
            Include questions covering: color theory, famous artists, techniques, art periods, and composition.
            Mix difficulty levels: 2 beginner (2 points each), 2 intermediate (3 points each), 1 advanced (4 points).
            Each question should have exactly 4 options."""
        }

        try:
            print(f"Generating questions for {subject}")
            response = client.chat.completions.create(
                model=config.MODEL,
                messages=[
                    {"role": "system", "content": "You are an expert educator creating assessment questions."},
                    {
                        "role": "user",
                        "content": subject_prompt[subject],
                    },
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "assessment_questions",
                        "schema": AssessmentQuestions.model_json_schema()
                    }
                }
            )
            raw_content = response.choices[0].message.content
            question_data = AssessmentQuestions.model_validate(json.loads(raw_content))
            for question in question_data.questions:
                DifficultyQuestions.objects.create(
                    subject = subject,
                    question_text = question.question,
                    answers = question.answer,
                    correct_answer = question.correct_answer,
                    difficulty_level = question.difficulty_level,
                    points = question.points
                )
            return {'success': True, 'questions': question_data.questions}
        
    
        except Exception as e:
            print(f"❌ Issue with AI question generator: {type(e).__name__}: {e}")
            return {'success': False} 

