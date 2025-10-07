from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import LearningProfile
from .models import Topic, Lesson
from .ai_lesson_generator import generate_lessons
import markdown

@login_required
def topic_list_view(request):
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject
    difficulty_level = profile.difficulty_level

    topics = Topic.objects.filter(
        subject = chosen_subject,
        difficulty_level = difficulty_level
    ).order_by('order')

    print("Profile subject:", profile.chosen_subject)
    print("Profile difficulty:", profile.difficulty_level)
    
    return render(request, 'topic_list.html', {'profile' : profile, 'topics': topics})
    
@login_required
def topic_detail_view(request, topic_id):
    topic = Topic.objects.get(id=topic_id)

    lessons = Lesson.objects.filter(topic = topic)

    print(f'Lesson count: {lessons.count()}, Topic: {topic}')

    if lessons.count() == 0:
        generate_lessons(
            topic_name=topic.topic_name,
            subject=topic.subject,
            difficulty_level=topic.difficulty_level
        )

        lessons = Lesson.objects.filter(topic = topic)
        print(f'Lesson generated: {lessons}')
    
    return render(request, 'topic_detail.html', {'topic': topic, 'lessons': lessons} )

@login_required
def lesson_detail_view(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)
    profile = request.user.learningprofile
 
    learning_styles = {
        'visual': profile.visual_learning_score,
        'hands_on': profile.hands_on_learning_score,
        'reading': profile.reading_learning_score
    }

    dominant_style = max(learning_styles, key=learning_styles.get)

    context = {
        'lesson': lesson,
        'topic': lesson.topic,
        'dominant_style': dominant_style,
    }
    
    return render(request, 'lesson_detail.html', context)
