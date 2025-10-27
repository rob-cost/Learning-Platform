from groq import Groq
from pydantic import BaseModel
from enum import Enum
from .models import Topic
from typing import List
import json
from dotenv import load_dotenv
from utils import config
from django.db import transaction
from django.contrib import messages
from learningPlatform.celery import app
from celery import shared_task


load_dotenv()

client = Groq()

class LevelEnum(str, Enum):
    beginner = 'beginner'
    intermediate = 'intermediate'
    advanced = 'advanced'

class SingleTopic(BaseModel):
    subject: str
    topic_name : str
    description: str
    order: int
    level: LevelEnum

class CollectionsTopics(BaseModel):
     topics: List[SingleTopic]

@shared_task
def generate_topic (subject):
         
        try:
            with transaction.atomic():
                Topic.objects.filter(subject = subject).delete()
                prompt = f"""Generate a comprehensive learning path for {subject}.

            Create exactly 10 topics for EACH difficulty level (beginner, intermediate, advanced).

            Requirements:
            - Beginner topics: Fundamentals and core concepts, assuming no prior knowledge
            - Intermediate topics: Building on basics, introducing more complex concepts
            - Advanced topics: Deep dive into sophisticated techniques and applications

            For each topic provide:
            - topic_name: Clear, descriptive title
            - description: 2-3 sentence explanation of what will be covered
            - order: Sequential number within that difficulty level (1-10)
            - subject: {subject}
            - level: Should be either of these values [beginner, intermediate, advanced]

            """

                response = client.chat.completions.create(
                            model=config.MODEL,

                            messages=[
                                {"role": "system", "content": "You are an expert educator creating topics for lessons."},
                                {
                                    "role": "user",
                                    "content": prompt,
                                },
                            ],
                            response_format={
                                "type": "json_schema",
                                "json_schema": {
                                    "name": "assessment_questions",
                                    "schema": CollectionsTopics.model_json_schema()
                                }
                            },
                            temperature=0.7
                        )
                    
                raw_content = response.choices[0].message.content
                topic_data = CollectionsTopics.model_validate(json.loads(raw_content))

                topics_to_create = [
                    Topic(
                        subject=single.subject,
                        topic_name=single.topic_name,
                        description=single.description,
                        difficulty_level=single.level.value, 
                        order=single.order
                    )
                    for single in topic_data.topics
                ]

                print(f'#####Saving topics ######')
                saved_topics = Topic.objects.bulk_create(topics_to_create)
                print(f'Saved topics: {saved_topics}')


                if len(saved_topics) == 30:
                    topic_ids = [topic.id for topic in saved_topics]
                    
                    # Schedule tasks using the correct app instance
                    def schedule_tasks():
                        for tid in topic_ids:
                            app.send_task(
                                'lessons.ai_lesson_generator.generate_lessons_task',
                                args=[tid]
                            )
                    
                    transaction.on_commit(schedule_tasks)

                return {'success': True}

        except Exception as e:
                print(f'❌ Issue with AI topic generator: {type(e).__name__}: {e}')
                messages.info(f'Error {e}, reload the page in few seconds' )
                return {'success': False}

