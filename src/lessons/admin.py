from django.contrib import admin
from .models import Topic, Lesson, UserProgress

# Register your models here.
@admin.register(Topic)
class AdminLearningProfile(admin.ModelAdmin):
    list_display=['subject', 'difficulty_level', 'topic_name', 'description']

@admin.register(Lesson)
class AdminLearningProfile(admin.ModelAdmin):
    list_display=['topic', 'lesson_title', 'lesson_content']

@admin.register(UserProgress)
class AdminLearningProfile(admin.ModelAdmin):
    list_display=['user', 'lesson', 'completed']
