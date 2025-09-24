from django.urls import path
from . import views

urlpatterns = [
    path('assessment/', views.learning_style_assessment_view, name='learning_style_assessment'),
]