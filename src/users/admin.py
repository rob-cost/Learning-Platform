from django.contrib import admin
from .models import LearningProfile

# Register your models here.
@admin.register(LearningProfile)
class AdminLearningProfile(admin.ModelAdmin):
    list_display=['user', 'visual_learning_score', 'hands_on_learning_score', 'reading_learning_score', 'chosen_subject', 'created_at', ]