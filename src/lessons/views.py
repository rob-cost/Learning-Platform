from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from users.models import LearningProfile
from .models import Topic


@login_required
def topic_list_view(request):
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject
    difficulty_level = profile.difficulty_level

    topics = Topic.objects.filter(
        subject = chosen_subject,
        difficulty_level = difficulty_level
    ).order_by('order')
    
    return render(request, 'topic_list.html', {'profile' : profile, 'topics': topics})
    


