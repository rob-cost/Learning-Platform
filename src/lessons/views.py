from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from users.models import LearningProfile
from .models import Topic, Lesson, UserProgress
from .ai_lesson_generator import generate_lessons_task
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
    completed_lessons = UserProgress.objects.filter(user = request.user, completed = True).values_list('lesson_id', flat=True)

    print(f'Lesson count: {lessons.count()}, Topic: {topic}')

    if lessons.count() == 0:
        generate_lessons_task.delay(
            topic.id
        )
        lessons_ready = False
        # no time to generate new questions and get them
        lessons = Lesson.objects.filter(topic = topic)
        print(f'Lesson generated: {lessons}')
    else:
        lessons_ready = True

    context = {
        'topic': topic, 
        'lessons': lessons, 
        'completed_lessons': completed_lessons,
        'lessons_ready' : lessons_ready
    }
    return render(request, 'topic_detail.html', context )

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

@login_required
def mark_lesson_completed(request, lesson_id):
    if request.method == "POST":
        lesson = get_object_or_404(Lesson, id = lesson_id)

        progress, _ = UserProgress.objects.get_or_create(user = request.user, lesson = lesson)

        if not progress.completed:
            progress.completed = True
            progress.completion_date = timezone.now()
            progress.save()
            messages.success(request, f"Lesson '{lesson.lesson_title}' marked as complete!")
        else:
            messages.info(request, f"You already completed '{lesson.lesson_title}'")
        
    return redirect('topic_detail', topic_id = lesson.topic.id )
