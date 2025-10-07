from groq import Groq
from pydantic import BaseModel
from .models import Topic
from typing import List
import json
from dotenv import load_dotenv
from .models import Lesson

load_dotenv()

client = Groq()

class LessonContent(BaseModel):
    visual_content: str
    hands_on_content: str
    reading_content: str

class SingleLesson(BaseModel):
    lesson_title: str
    order: int
    visual_content: str
    hands_on_content: str
    reading_content: str
    estimated_duration: int

class LessonCollection(BaseModel):
    subject: str
    lessons: List[SingleLesson]


def generate_lessons(topic_name, subject, difficulty_level):

    top_obj = Topic.objects.get(
             topic_name = topic_name,
             subject = subject,
             difficulty_level = difficulty_level
        )

    lesson_count = Lesson.objects.filter(topic = top_obj).count()
    if lesson_count == 4:
         return 
    if lesson_count >= 0:
        Lesson.objects.filter(topic = top_obj).delete()
        prompt = f"""Create 4 comprehensive lessons for the topic: "{topic_name}" 
        
                    Subject: {subject}
                    Difficulty Level: {difficulty_level}

                    For each lesson, provide content in THREE distinct learning styles:

                    1. VISUAL_CONTENT:
                    - Diagrams, charts, or visual metaphors (described in text)
                    - Step-by-step visual breakdowns
                    - Conceptual illustrations
                    - Use clear headers and bullet points for visual scanning
                    - Start with a clear overview diagram description
                    - Include 3-4 visual examples or metaphors
                    - Provide step-by-step visual breakdowns

                    2. HANDS_ON_CONTENT:
                    - Practical exercises and activities
                    - Code examples (for programming) or practice problems
                    - Interactive challenges
                    - Real-world application tasks
                    - "Try this" activities

                    3. READING_CONTENT:
                    - Detailed theoretical explanations
                    - In-depth analysis and context
                    - Background information
                    - Comprehensive written descriptions
                    - Key concepts and definitions

                    Requirements:
                    - Each lesson must contain ALL three content types
                    - Each content section should be at least 300-500 words
                    - Provide comprehensive, detailed explanations with multiple examples
                    - Ensure logical progression across the 4 lessons
                    - Include at least 3 concrete, real-world examples for each concept
                    - Provide code snippets with detailed line-by-line explanations
                    - Make content appropriate for {difficulty_level} level
                    - Each lesson should take approximately from 20 to 50 minutes to complete
                    - Number lessons sequentially (order: 1, 2, 3, 4)

                    Provide clear, engaging content that works for different learning preferences."""

        try:
            response = client.chat.completions.create(
               model="openai/gpt-oss-20b",
                messages=[
                    {"role": "system", "content": "You are an expert educational content creator who designs multi-modal learning experiences."},
                    {"role": "user", "content": prompt}
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "lesson_collection",
                        "schema": LessonCollection.model_json_schema()
                    }
                },
                temperature=0.8
            )
            raw_content = response.choices[0].message.content
            lessons_data = LessonCollection.model_validate(json.loads(raw_content))
            for lesson in lessons_data.lessons:
                Lesson.objects.create(
                    topic = top_obj,
                    lesson_title = lesson.lesson_title,
                    order = lesson.order,
                    estimated_duration = lesson.estimated_duration,
                    lesson_content = {'visual_learning': lesson.visual_content, 'hands_on_learning': lesson.hands_on_content, 'reading_learning': lesson.reading_content}
                )
            
        
        except Exception as e:
                print(f"❌ Issue with AI question generator: {type(e).__name__}: {e}")
                return []
