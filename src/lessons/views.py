from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Topic, Lesson, UserProgress
from .ai_lesson_generator import generate_lessons_task
from django.http import JsonResponse
import asyncio
from django.core.cache import cache
    
@login_required
def topic_detail_view(request, topic_id):
    topic = Topic.objects.get(id = topic_id)
    lessons = Lesson.objects.filter(topic_id = topic_id) 

    completed_lessons = UserProgress.objects.filter(user = request.user, completed = True).values_list('lesson_id', flat=True)
    
    lessons_exist = lessons.count() == 4

    generate_lessons_task.delay(topic_id)
    
    context = {
        'topic': topic, 
        'lessons': lessons, 
        'completed_lessons': completed_lessons,
        'lessons_exist': lessons_exist
    }
    return render(request, 'topic_detail.html', context )

@login_required
def check_lessons_status(request, topic_id):
    try:
        lessons_count = Lesson.objects.filter(topic__id=topic_id).count()
        print(f'lessons n: {lessons_count}')
        error = cache.get(f'lessons_for_topic_{topic_id}')
        if not error and lessons_count != 4:
            return JsonResponse({'error': 'Lessons not ready'})
        return JsonResponse({"ready": lessons_count == 4})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    
@login_required
def lesson_detail_view(request, lesson_id):
    lesson = Lesson.objects.get(id=lesson_id)

    context = {
        'lesson': lesson,
        'topic': lesson.topic,
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


    