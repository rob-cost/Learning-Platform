from groq import Groq
from pydantic import BaseModel
from .models import Topic
from typing import List
import json
from dotenv import load_dotenv
from .models import Topic

load_dotenv()

client = Groq()

class SingleTopic(BaseModel):
    topic_name : str
    description: str
    order: int

class CollectionsTopics(BaseModel):
     subject: str
     beginner_topics: List[SingleTopic]
     intermediate_topics: List[SingleTopic]
     advanced_topics: List[SingleTopic]

def generate_topic (subject):

    topic_count = Topic.objects.filter(subject = subject).count()
    if topic_count == 30:
         return None
    
    if topic_count < 30 :
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

    Structure your response with three separate lists: beginner_topics, intermediate_topics, and advanced_topics."""

        try:
            response = client.chat.completions.create(
                    model="openai/gpt-oss-20b",
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
            print(f'Topic data: {topic_data}')
            for topic in topic_data.beginner_topics:
                Topic.objects.create(
                    subject = subject,
                    topic_name = topic.topic_name,
                    description = topic.description,
                    order = topic.order,
                    difficulty_level = 'beginner'
                )
            for topic in topic_data.intermediate_topics:
                Topic.objects.create(
                    subject = subject,
                    topic_name = topic.topic_name,
                    description = topic.description,
                    order = topic.order,
                    difficulty_level = 'intermediate'
                )
            for topic in topic_data.advanced_topics:
                Topic.objects.create(
                    subject = subject,
                    topic_name = topic.topic_name,
                    description = topic.description,
                    order = topic.order,
                    difficulty_level = 'advanced'
                )
            return topic_data

        except Exception as e:
                print(f"❌ Issue with AI topic generator: {type(e).__name__}: {e}")
                return None



