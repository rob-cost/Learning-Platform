from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('style-assessment/', views.learning_style_assessment_view, name='learning_style_assessment'),
    path('subject-selection/', views.subject_selection_view, name='subject_selection'),
    path('difficulty-assessment/', views.difficulty_assessment_view, name='difficulty_assessment'),
    path('retake-assessment/', views.retake_assessment_view, name='retake_assessment'),
    path('level-choice/', views.level_choice_view, name='level_choice'),
    path('next-topic/', views.next_topic_view, name='next_topic'),
    path('dashboard/', views.landing_view, name='landing'),
    path('profile/', views.profile_view, name='profile_page')
]