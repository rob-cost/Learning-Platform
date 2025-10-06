# test_topic_generation.py (in project root, not in lessons app)
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'learningPlatform.settings')
django.setup()

# Now you can import after Django is set up
from lessons.ai_topic_generator import generate_topic

# Test it
generate_topic('art')
print("Topics generated successfully!")