from django.db import models
from django.contrib.auth.models import User

SUBJECT_CHOICES = [
        ('programming', 'Programming and software development'),
        ('music', 'Musical theory and composition'),
        ('art', 'Art history and art crafting')
    ]


# Create your models here.
class LearningProfile(models.Model):

    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced')
    ]

    #user profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    #points for each learning method style
    visual_learning_score = models.PositiveIntegerField(default=0)
    hands_on_learning_score = models.PositiveIntegerField(default=0)
    reading_learning_score = models.PositiveIntegerField(default=0)

    #choose a subject
    chosen_subject = models.CharField(max_length=50, choices=SUBJECT_CHOICES)

    #assessment result
    assessment_score = models.PositiveIntegerField(default=0, help_text="from 0 to 100")
    difficulty_level = models.CharField(max_length=13, choices=DIFFICULTY_CHOICES, default='beginner')
    difficulty_assessment_completed = models.BooleanField(default=False)
    difficulty_assessment_date = models.DateTimeField(null=True, blank=True)

    registration_step = models.IntegerField(default=1)
    registration_completed = models.BooleanField(default=False)

    learning_pace = models.FloatField(default=0.0, help_text='Lessons completed per week')

    pace_last_calculated = models.DateTimeField(null=True, blank=True)

    #timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_learning_style_scores(self):
        return {
            'visual': self.visual_learning_score,
            'hands_on': self.hands_on_learning_score,
            'reading': self.reading_learning_score
        }

    def __str__(self):
        return f"{self.user.username}'s learning profile"
    

    