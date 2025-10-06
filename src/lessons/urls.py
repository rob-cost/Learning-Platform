from django.urls import path
from . import views

urlpatterns = [
    path('topics/', views.topic_list_view, name='topic_list' ),
]