from django.urls import path
from . import views

urlpatterns = [
    path('style-assessment/', views.learning_style_assessment_view, name='learning_style_assessment'),
    path('subject-selection/', views.subject_selection_view, name='subject_selection'),
    path('difficulty-assessment/', views.difficulty_assessment_view, name='difficulty_assessment'),
    path('signup/', views.signup_view, name='signup'),
    path('dashboard/', views.landing_view, name='landing'),
    path('profile/', views.profile_view, name='profile_page')
]