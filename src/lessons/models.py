from django.db import models
from django.contrib.auth.models import User
from typing import List

SUBJECT_CHOICES = [
        ('programming', 'Programming and software development'),
        ('music', 'Musical theory and composition'),
        ('art', 'Art history and art crafting'),
        ('mathematics', 'Mathematics and problem solving'),
        ('languages', 'Foreign languages and linguistics'),
        ('science', 'Natural sciences and physics'),
        ('business', 'Business and entrepreneurship'),
        ('cooking', 'Cooking and culinary arts'),
        ('photography', 'Photography and visual media'),
        ('fitness', 'Fitness and exercise science'),
        ('philosophy', 'Philosophy and critical thinking'),
        ('history', 'World history and civilization'),
        ('psychology', 'Psychology and human behavior'),
        ('design', 'Graphic design and UI/UX'),
        ('marketing', 'Digital marketing and social media'),
    ]

DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]

class Topic (models.Model):
    subject = models.CharField(max_length= 50, choices=SUBJECT_CHOICES)
    difficulty_level = models.CharField(max_length=50, choices=DIFFICULTY_CHOICES)
    topic_name = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(help_text='Order within the difficulty level')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['difficulty_level', 'order']
        unique_together = ['subject', 'difficulty_level', 'order']
     
    def __str__(self):
        return f"{self.subject} - {self.difficulty_level} - {self.topic_name}"
        

class Lesson (models.Model):
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='lessons')
    lesson_title = models.CharField(max_length=200)
    lesson_content = models.JSONField(help_text="AI-generated lesson content based on skills")
    order = models.IntegerField(help_text="Order within the topic")
    estimated_duration = models.IntegerField(default=30, help_text="Estimated minutes to complete")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta: 
        ordering = ['topic', 'order']
        unique_together = ['topic', 'order']
    
    def __str__(self):
        return f"{self.topic.topic_name} - Lesson {self.order}: {self.lesson_title}"

class UserProgress (models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(null=True, blank=True)
    time_spent = models.IntegerField(default=0, help_text="Minutes spent on lesson")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'lesson']
    
    def __str__(self):
        return f"{self.user.username} - {self.lesson.lesson_title} - {'Completed' if self.completed else 'In Progress'}"