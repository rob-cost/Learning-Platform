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
        return {'successful': True, 'reason': 'Lessons already exist'}
    
    else:

        try:
            
            with transaction.atomic():

                Lesson.objects.filter(topic = topic_id).delete()
                
                prompt = f"""Create 4 comprehensive lessons for the topic: "{topic.topic_name}" 
                
                            Subject: {topic.subject}
                            Difficulty Level: {topic.difficulty_level}

                            CONTENT GUIDELINES:
                            - Produce lessons that build progressively in difficulty and depth.
                            - Each lesson must have:
                            • A clear and engaging title.
                            • Number lessons sequentially (order: 1, 2, 3, 4)
                            • Ensure logical progression across the 4 lessons
                            - Each lesson's content must be between **600-800 words** long.
                            - Content must include:
                            • Clear explanations of key ideas and concepts.
                            • At least 2-3 real-world examples relevant to the topic.
                            • Smooth transitions suitable for {topic.difficulty_level} learners.
                            - Each lesson should take approximately 20–40 minutes to complete.

                            FORMATTING RULES:
                            - Use Markdown formatting: # headers, **bold**, *italic*, lists, etc.
                            - For code blocks, use triple backticks with language: ```python
                            - Use bullet points with - or * for lists
                            - Use numbered lists with 1. 2. 3.
                            
                            CRITICAL - JSON ESCAPE RULES (VERY IMPORTANT):
                            - Do NOT use single backslashes (\\) anywhere in the content
                            - Property name must be enclosed in double quotes
                            - For line breaks in content, use actual newlines, not \\n escape sequences
                            - For tabs, use actual spaces, not \\t
                            - Never use regex patterns or escape sequences like \\d \\w \\s in examples
                            - If discussing backslashes, write them as "backslash character" in words
                            - Avoid any LaTeX or mathematical notation with backslashes
                            - Do not include file paths with backslashes (use forward slashes if needed)
                            - The content should be plain text with Markdown, no special escape sequences
                        
                        Return complete JSON with all 4 lessons.

                            LessonCollection = {{
                            "subject": "{topic.subject}",
                            "lessons": [
                                {{
                                "lesson_title": "<string>",
                                "order": <1-4>,
                                "content": "<Markdown-formatted string, between 600 and 800 words>",
                                "estimated_duration": <integer between 10 and 50>
                                }},
                                ...
                            ]
                            }}
                            CRITICAL: Ensure complete JSON. Do not truncate.
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
                    temperature=0.7,
                    max_tokens=10000
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
                return {'successful': True, 'reason': 'Lessons created successfuly'}

        except Exception as e:
            print(f"❌ Issue with AI lesson generator: {type(e).__name__}: {e}")
            return {'successful': False, 'reason': str(e)}
    


@shared_task(bind=True, max_retries=1, default_retry_delay=5)
def generate_lessons_task(self, topic_id):
    try:
        topic = Topic.objects.get(id=topic_id)

        if topic.status != 'pending':
            topic.status = 'pending'
            topic.save()
        
        result = generate_lessons_for_topic(topic_id)

        if result is None:
            print(f"❌ generate_lessons_for_topic returned None for topic {topic_id}")
        
        if not result['successful']:
            reason = result.get('reason', 'Unknown failure')
            print(f"❌ Task failed for topic {topic_id}: {reason}")
            
            # Check if this is the last retry
            if self.request.retries >= self.max_retries:
                topic.status = 'failed'
                topic.save()
                print(f'🔴 Topic {topic_id} marked as FAILED after all retries')
                return {'successful': False, 'reason': reason}
            
            # Still have retries, raise to retry
            raise self.retry(exc=Exception(reason))
        
        # Success!
        topic.status = 'success'
        topic.save()
        print(f"✅ Lessons successfully generated for topic {topic_id}")
        return result
    
    except Exception as e:
        topic = Topic.objects.get(id=topic_id)
        
        if self.request.retries >= self.max_retries:
            topic.status = 'failed'
            topic.save()
            print(f"🔴 Topic {topic_id} marked as FAILED due to exception: {str(e)}")
        
        raise


