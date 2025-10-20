from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage_view, name='homepage'),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.logout_view, name='logout'),
    path('subject-selection/', views.subject_selection_view, name='subject_selection'),
    path('difficulty-assessment/', views.difficulty_assessment_view, name='difficulty_assessment'),
    path('retake-assessment/', views.retake_assessment_view, name='retake_assessment'),
    path('level-choice/', views.level_choice_view, name='level_choice'),
    path('next-topic/', views.next_topic_view, name='next_topic'),
    path('dashboard/', views.landing_view, name='landing'),
    path('profile/', views.profile_view, name='profile_page'),
    path('profile-settings/', views.profile_settings_view, name='profile_settings'),
    path('check-username/', views.check_username_availability, name='check_username'),
    path('delete-profile/', views.delete_profile_view, name='delete_profile'),
    path('profile/status/', views.check_topic_status, name='check_topic_status'),


]