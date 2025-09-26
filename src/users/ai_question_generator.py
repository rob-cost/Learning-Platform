from groq import Groq
from pydantic import BaseModel
from typing import Literal, List
import json

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


def generate_difficulty_questions(subject):
    subject_prompt = {
        'programming': """ Generate 5 multiple choice questions to assess programming knowledge level. 
        Include questions covering: basic syntax, variables, functions, loops, and problem-solving. 
        Mix difficulty levels: 2 beginner (2 points each), 2 intermediate (3 points each), 1 advanced (4 points).
        Each question should have exactly 4 options.""",
        'music': """ Generate 5 multiple choice questions to assess musical theory and composition knowledge.
        Include questions covering: notes, scales, rhythm, harmony, and basic composition.
        Mix difficulty levels: 2 beginner (2 points each), 2 intermediate (3 points each), 1 advanced (4 points).
        Each question should have exactly 4 options.""",
        'art': """Generate 5 multiple choice questions to assess art history and crafting knowledge.
        Include questions covering: color theory, famous artists, techniques, art periods, and composition.
        Mix difficulty levels: 2 beginner (2 points each), 2 intermediate (3 points each), 1 advanced (4 points).
        Each question should have exactly 4 options."""
    }

    try:
        print(f"Generating questions for {subject}")
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
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
        print("✅ Got response from Groq")
        raw_content = response.choices[0].message.content
        question_data = AssessmentQuestions.model_validate(json.loads(raw_content))
        return question_data.questions
        
    
    except Exception as e:
        print(f"❌ Issue with AI question generator: {type(e).__name__}: {e}")
        return []
        # possible fallbak questions can be added 

