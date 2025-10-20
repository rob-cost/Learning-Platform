from django.db import models
from django.contrib.auth.models import User

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

# Create your models here.
class LearningProfile(models.Model):

    #user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #choose a subject
    chosen_subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)

    #assessment result
    assessment_score = models.PositiveIntegerField(default=0, help_text="from 0 to 100")
    difficulty_level = models.CharField(max_length=13, choices=DIFFICULTY_CHOICES, default='beginner')
    difficulty_assessment_ready = models.BooleanField(default=False)
    difficulty_assessment_completed = models.BooleanField(default=False)
    difficulty_assessment_date = models.DateTimeField(null=True, blank=True)

    registration_step = models.IntegerField(default=1)
    registration_completed = models.BooleanField(default=False)

    learning_pace = models.FloatField(default=0.0, help_text='Lessons completed per week')

    pace_last_calculated = models.DateTimeField(null=True, blank=True)

    #timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def __str__(self):
        return f"{self.user.username}'s learning profile"
    

    
class DifficultyQuestions(models.Model):
    subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES, help_text="topic's subject")
    question_text = models.TextField(help_text="The question users will answer")
    answers = models.JSONField(help_text="options answers")
    correct_answer = models.IntegerField(choices=[(0, 'A'), (1, 'B'), (2, 'C'), (3, 'D')])
    difficulty_level = models.CharField(max_length=40, choices=DIFFICULTY_CHOICES)
    points = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)