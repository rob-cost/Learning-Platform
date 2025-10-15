from groq import Groq
from pydantic import BaseModel
from .models import Topic, Lesson
from typing import List
import json
from dotenv import load_dotenv
from utils import config
import markdown2
from django.db import transaction
import threading


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

def markdown_to_html(md_text: str) -> str:
    return markdown2.markdown(
         md_text, extras=[
            "fenced-code-blocks",   # Properly render ```python ... ```
            "tables",               # Render markdown tables
            "strike",               # Support ~~strikethrough~~
            "task_list",            # Render task lists [x]
            "code-friendly",        # Don’t mess with inline code
            "break-on-newline",     # Handle single newlines gracefully
            "cuddled-lists",        # Avoid gaps between lists
        ]
    ) 


def generate_lessons_threading(topic_id):

    # problem: more user can access the same topic 
    topic = Topic.objects.get(id = topic_id)

    try:
        topic.status = 'pending'
        topic.error_message = None
        topic.save(update_fields=['status', 'error_message'])

        lesson_count = Lesson.objects.filter(topic = topic).count()
    
        if lesson_count == 4:
            pass 
        
        with transaction.atomic():

            Lesson.objects.filter(topic = topic).delete()
            
            prompt = f"""Create 4 comprehensive lessons for the topic: "{topic.topic_name}" 
            
                        Subject: {topic.subject}
                        Difficulty Level: {topic.difficulty_level}

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
                        - Make content appropriate for {topic.difficulty_level} level
                        - Each lesson should take approximately from 20 to 50 minutes to complete
                        - Number lessons sequentially (order: 1, 2, 3, 4)
                        - Use valid Markdown for headings, lists, bold, italics, and code blocks
                        - Code blocks: wrap code in triple backticks ``` with language, do NOT escape newlines
                        - Do NOT escape Markdown characters (no `\\n`, `\\` for backticks)

                        Provide clear, engaging content that works for different learning preferences."""
            response = client.chat.completions.create(
            model=config.MODEL,
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
                temperature=0.7
            )
            raw_content = response.choices[0].message.content
            lessons_data = LessonCollection.model_validate(json.loads(raw_content))

            for lesson in lessons_data.lessons:
                html_visual = markdown_to_html(lesson.visual_content)
                html_hands_on = markdown_to_html(lesson.hands_on_content)
                html_reading = markdown_to_html(lesson.reading_content)
                Lesson.objects.create(
                    topic = topic,
                    lesson_title = lesson.lesson_title,
                    order = lesson.order,
                    estimated_duration = lesson.estimated_duration,
                    lesson_content = {'visual_content': html_visual, 'hands_on_content': html_hands_on, 'reading_content': html_reading}
                )


        topic.status = "ready"
        topic.save(update_fields=['status']) 
        print(f"✅ Lessons successfully generated for topic: {topic.topic_name}")
        
                
    except Exception as e:
        topic.status = "not ready"
        topic.error_message = str(e)
        topic.save(update_fields=['status', 'error_message'])
        print(f"❌ Issue with AI {e} question generator: {type(e).__name__}: {e}")

 
def start_lesson_generation(topic_id):
    thread = threading.Thread(target=generate_lessons_threading, args=(topic_id,))
    thread.daemon = True  # Thread will stop when main program exits
    thread.start()
