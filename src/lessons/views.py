from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Topic, Lesson, UserProgress
from .ai_lesson_generator import generate_lessons_task
from django.http import JsonResponse
import asyncio
    
@login_required
def topic_detail_view(request, topic_id):
    topic = Topic.objects.get(id=topic_id)
    completed_lessons = UserProgress.objects.filter(user = request.user, completed = True).values_list('lesson_id', flat=True)

    lessons = Lesson.objects.filter(topic = topic) 

    if lessons.count() != 4:
        generate_lessons_task.delay(topic.id) 
        lessons_ready = False
    else:
        lessons_ready = True

    context = {
        'topic': topic, 
        'lessons': lessons, 
        'completed_lessons': completed_lessons,
        'lessons_ready': lessons_ready
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


@login_required
def check_lessons_status(request, topic_id):
    topic = Topic.objects.get(id = topic_id)
    lessons_count = Lesson.objects.filter(topic__id=topic_id).count()
    return JsonResponse({"ready": lessons_count == 4 and topic.status == "ready",
        "count": lessons_count,
        "error": topic.status == "not ready",
        "error_message": topic.error_message,})