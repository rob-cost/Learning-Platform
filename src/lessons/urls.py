from django.urls import path
from . import views

urlpatterns = [
 
    path('topic/<int:topic_id>/', views.topic_detail_view, name='topic_detail' ),
    path('lesson/<int:lesson_id>/', views.lesson_detail_view, name='lesson_detail' ),
    path('lesson/<int:lesson_id>/complete/', views.mark_lesson_completed, name='mark_lesson_complete'),
    path('topic/<int:topic_id>/status/', views.check_lessons_status, name='check_lessons_status'),

]
