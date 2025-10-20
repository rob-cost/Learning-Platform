from groq import Groq
from pydantic import BaseModel
from .models import Topic, Lesson
from typing import List
import json
from dotenv import load_dotenv
from utils import config
import markdown2
from django.db import transaction
from celery import shared_task
import asyncio
from django.core.cache import cache


load_dotenv()

client = Groq()


class SingleLesson(BaseModel):
    lesson_title: str
    order: int
    content: str
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


def generate_lessons_for_topic(topic_id):

    # problem: more user can access the same topic 
    topic = Topic.objects.get(id = topic_id)
    lessons = Lesson.objects.filter(topic_id = topic_id)

    if lessons.count() == 4:
        return
    
    else:

        try:
            
            with transaction.atomic():

                Lesson.objects.filter(topic = topic_id).delete()
                
                prompt = f"""Create 4 comprehensive lessons for the topic: "{topic.topic_name}" 
                
                            Subject: {topic.subject}
                            Difficulty Level: {topic.difficulty_level}

                            Instructions:
                            - Produce lessons that build progressively in difficulty and depth.
                            - Each lesson must have:
                            • A clear and engaging title.
                            • Number lessons sequentially (order: 1, 2, 3, 4)
                            • Ensure logical progression across the 4 lessons
                            • A single unified content block (can be sub-divided in chapters).
                            • The content should be detailed, educational, and cohesive.
                            - Each lesson's content must be at least **1000 words** long.
                            - Content must include:
                            • Clear explanations of key ideas and concepts.
                            • At least 3 real-world examples relevant to the topic.
                            • Optional code snippets or applied demonstrations if relevant to the subject.
                            • Smooth transitions and logical flow suitable for {topic.difficulty_level} learners.
                            - Use valid Markdown for formatting (headings, lists, bold, italics, code blocks).
                            - Wrap code in triple backticks ``` with the language name, and do NOT escape newlines or Markdown characters.
                            - The tone should be clear, engaging, and instructive, as if written by an expert educator.
                            - Each lesson should take approximately 15–40 minutes to complete.

                            Provide clear, engaging content that works for different learning preferences.
                            Return the data strictly in JSON format matching this structure:

                            LessonCollection = {{
                            "subject": "{topic.subject}",
                            "lessons": [
                                {{
                                "lesson_title": "<string>",
                                "order": <1-4>,
                                "content": "<Markdown-formatted string, at least 1000 words>",
                                "estimated_duration": <integer between 10 and 50>
                                }},
                                ...
                            ]
                            }}
                            """
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

                lessons = lessons_data.lessons

                if len(lessons) != 4:
                    return {'successful': False, 'reason': f'Expected 4 lessons, got {len(lessons)}'}

            
                lesson_objects = [
                    Lesson(
                        topic=topic,
                        lesson_title=lesson.lesson_title,
                        order=lesson.order,
                        estimated_duration=lesson.estimated_duration,
                        lesson_content=markdown_to_html(lesson.content)
                    )
                    for lesson in lessons
                ]

                Lesson.objects.bulk_create(lesson_objects)
                return {'successful': True}

        except Exception as e:
            print(f"❌ Issue with AI lesson generator: {type(e).__name__}: {e}")
            cache.set(f'lessons_for_topic_{topic_id}', False, 9)
            return {'successful': False, 'reason': str(e)}
    


@shared_task (bind=True, max_retries=3, default_retry_delay=240)
def generate_lessons_task(self, topic_id):
    result = generate_lessons_for_topic(topic_id)
    if not result ['successful']:
        reason = result.get('reason', 'Unknown failure')
        print(f"❌ Task failed for topic {topic_id}: {reason}")
        raise self.retry(exc=Exception(reason))

    print(f"✅ Lessons successfully generated for topic {topic_id}")
    return result


