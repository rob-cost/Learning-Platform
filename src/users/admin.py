from django.contrib import admin
from .models import LearningProfile, DifficultyQuestions

# Register your models here.
@admin.register(LearningProfile)
class AdminLearningProfile(admin.ModelAdmin):
    list_display=['user', 'chosen_subject', 'created_at', ]

@admin.register(DifficultyQuestions)
class AdminDifficultyQuestions(admin.ModelAdmin):
    list_display=['subject', 'question_text', 'answers']