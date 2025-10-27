from .forms import SubjectSelectionForm, DifficultyAssessmentForm, ProfileSettingsForm
from .models import LearningProfile, DifficultyQuestions, User
from lessons.models import Topic, Lesson, UserProgress
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.views import PasswordChangeView
from django.contrib.auth.forms import UserCreationForm
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from .ai_question_generator import generate_difficulty_questions
from lessons.ai_topic_generator import generate_topic
from lessons.ai_lesson_generator import generate_lessons_task
from django.http import JsonResponse
from learningPlatform.celery import app

user_answers = []

def homepage_view(request):
    return render(request, 'homepage.html')

@login_required
def landing_view(request):
    try:
        profile = request.user.learningprofile
        step = profile.registration_step

        if step == 1:
            return redirect('subject_selection')
        if step == 2:
            return redirect('difficulty_assessment')
        else:
            return redirect('profile_page')
    except LearningProfile.DoesNotExist:
        LearningProfile.objects.create(user = request.user)
        return redirect('subject_selection')
    
def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            LearningProfile.objects.create(user = user)
            login(request, user)
            return redirect('subject_selection')
    else: 
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'You have successfuly logged out!')
    return redirect('login')

@login_required
def subject_selection_view(request):

    profile = request.user.learningprofile
    if profile.registration_step != 1:
        return redirect('landing')

    if request.method == 'POST':
        print('User completed the subject form')

        form = SubjectSelectionForm(request.POST)

        if form.is_valid():
            chosen_subject = form.cleaned_data['chosen_subject']
            print(f'user choose: {chosen_subject}')

            profile = LearningProfile.objects.get(user=request.user)
            profile.chosen_subject = chosen_subject
            profile.registration_step = 2
            profile.save()

            # Starts creating topics in the background
            if not Topic.objects.filter(subject = profile.chosen_subject).exists():
                app.send_task('lessons.ai_topic_generator.generate_topic', args=[chosen_subject])
                

            return redirect('difficulty_assessment') 
    
    else:
        form = SubjectSelectionForm()

    return render(request, 'subject_selection.html', {'form': form})

@login_required
def difficulty_assessment_view(request):
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject
    is_retake = request.session.get('retake_assessment', False)

    if profile.registration_step != 2 and not is_retake:
        return redirect('landing')
    
    questions_data = generate_difficulty_questions(chosen_subject, is_retake)
    questions_exists = DifficultyQuestions.objects.filter(subject = chosen_subject).exists()

    if not questions_data['success']:
        messages.error(request, f'Error in generating assessment. Please try again later.')
        return redirect('login')

    if request.method == "POST":
        form = DifficultyAssessmentForm(questions_data['questions'], request.POST)
        if form.is_valid():
            assessment_score = form.get_user_answers_with_correct()

            if assessment_score > 80:
                new_level = 'advanced'
            elif assessment_score >50:
                new_level = 'intermediate'
            else:
                new_level = 'beginner'

            if is_retake:
                previous_level = request.session.get('previous_level')
                level_order = {
                    'beginner': 1,
                    'intermediate': 2,
                    'advanced': 3
                }
                if level_order[new_level] > level_order[previous_level]:
                    request.session['new_level'] = new_level
                    request.session['new_score'] = assessment_score
                    return redirect('level_choice')
                
                profile.assessment_score = assessment_score
                profile.save()
                messages.info(request, f'Assessment completed. You scored: {assessment_score}. You remain at {previous_level} level.')
                request.session.pop('retake_assessment', None) 
                return redirect('profile_page')
            
            profile.assessment_score = assessment_score
            profile.difficulty_level = new_level
            profile.difficulty_assessment_completed = True
            profile.registration_step = 3
            profile.save()

            messages.success(request, "Well done you have completed the registration process!")
            return redirect('profile_page') 
    else:
        form = DifficultyAssessmentForm(questions_data['questions'])
    return render(request, 'difficulty_assessment.html', {'form': form, 'questions_exists': questions_exists})

@login_required
def profile_view(request):
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject
    difficulty_level = profile.difficulty_level

    # get error mess from request
    code_msg = request.GET.get("error")
    error_msg = {
        'ai_timeout': 'AI is taking longer than usual, please try again in a bit.',
    }
    if code_msg:
        messages.info(request, error_msg[code_msg])

    # creates topics if they don'exist yet
    if Topic.objects.filter(subject = chosen_subject, difficulty_level = difficulty_level).count() != 10:
       app.send_task('lessons.ai_topic_generator.generate_topic', args=[chosen_subject])
    
    # display topics in order
    topics = Topic.objects.filter(
        subject = chosen_subject,
        difficulty_level = difficulty_level
    ).order_by('order')    

    # check if a topic has been completed
    for topic in topics:
        lessons_topic = Lesson.objects.filter(topic = topic)
        completed_count = UserProgress.objects.filter(user = request.user, lesson__in = lessons_topic, completed = True ).count()
        if lessons_topic.count() == completed_count and lessons_topic.count() != 0:
            topic.is_completed = True
        else:
            topic.is_completed = False
    
    # calculate progress percentage of user
    expected_lessons = 40
    completed_lessons = UserProgress.objects.filter(user = request.user, lesson__topic__in = topics, completed = True).count()
    progress_percentage = round(completed_lessons / expected_lessons * 100)

    request.session['progress_percentage'] = progress_percentage

    if progress_percentage == 100 and not request.session.get('complete_notified', False):
        return redirect('next_topic')

    if progress_percentage < 100:
        request.session.pop('complete_notified', None)

    context = {
        'profile' : profile,
        'username' : request.user.username,
        'topics': topics,
        'total_lessons': expected_lessons,
        'completed_lessons': completed_lessons,
        'progress_percentage': progress_percentage
        }
 
    return render(request, 'profile.html', context)

@login_required
def profile_settings_view(request):
    if request.method == "POST":
        form = ProfileSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, f'Profile updated successfully')
            return redirect('profile_page')
        else:
            messages.error(request, f'A user with that username already exists.')
            return redirect('profile_page')
        
    else:
        form = ProfileSettingsForm(instance=request.user)
        return render(request, 'profile_settings.html', {'form': form})

@login_required
def check_username_availability(request):
    username = request.GET.get('username', '')
    current_user_id = request.user.id
    
    # Check if username exists (excluding current user)
    exists = User.objects.filter(username=username).exclude(id=current_user_id).exists()
    
    return JsonResponse({
        'available': not exists
    })

@login_required
def delete_profile_view(request):    
    if request.method == 'POST':
        try:
            user = request.user
            logout(request)
            user.delete()

            messages.success(request, f'Profile successfuly  deleted')
            return redirect('signup')
        
        except Exception as e:
            messages.error(request, f'Error! Please try again later')
            print(f'Error: {e}')
            return redirect('profile_page')
    return redirect('profile_settings')
    
 
@login_required
def retake_assessment_view(request):
    profile = request.user.learningprofile
    progress_percentage = request.session.get('progress_percentage')

    if progress_percentage > 79:
        request.session["retake_assessment"] = True
        request.session["previous_level"] = profile.difficulty_level
        request.session["previous_score"] = profile.assessment_score

        return redirect('difficulty_assessment')
    else:
        messages.info(request, f'Complete at least 80% of the program')
        return redirect('profile_page')

@login_required
def level_choice_view(request):
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject
    new_level = request.session.get('new_level')
    new_score = request.session.get('new_score')

    if request.method == "POST":
        choice = request.POST.get('choice')

        if choice =='update':
            profile.assessment_score = new_score
            profile.difficulty_level = new_level
            profile.save()
            generate_topic(chosen_subject)
            messages.success(request, f"Your level has been updated to {new_level.capitalize()}!")
        else:
            messages.info(request, f'You kept your previous level')
        
        request.session.pop('new_level', None)
        request.session.pop('new_score', None)
        request.session.pop('retake_assessment', None)
            
        return redirect('profile_page')
    
    context = {
        'new_level' : new_level,
        'new_score' : new_score,
        'previous_level' : profile.difficulty_level,
        'previous_score' : profile.assessment_score
    }
    return render(request, 'level_choice.html', context )

@login_required
def next_topic_view(request):
    profile = request.user.learningprofile
    current_difficulty_level = profile.difficulty_level

    if request.method == "POST":
        if current_difficulty_level == "advanced":
            messages.info(request, f'Well done {request.user.username}. You have successfully completed the course!')
        
        else:
            next_difficulty_level = {'beginner' : 'intermediate', 'intermediate': 'advanced'}
            profile.difficulty_level = next_difficulty_level[current_difficulty_level]
            profile.save()
            messages.info(request, f'Well done {request.user.username}! You advanced level')

        request.session['complete_notified'] = True 
        return redirect('profile_page')
    
    context = {
        'current_level': current_difficulty_level,
        'username': request.user.username
    }
    return render(request, 'next_topic.html', context)


# -- API CALL VIEWS -- 

@login_required
def topic_lesson_status(request):
    profile = request.user.learningprofile
    topics = Topic.objects.filter(subject = profile.chosen_subject, difficulty_level = profile.difficulty_level)
    
    topics_with_lessons = []
    for topic in topics:
        topics_with_lessons.append({
            'id': topic.id,
            'topic_status': topic.status
        })
    
    return JsonResponse({
        'topics': topics_with_lessons
    })

@login_required
def profile_topic_status_view(request):
    try:
        profile = request.user.learningprofile
        topics_count = Topic.objects.filter(subject = profile.chosen_subject, difficulty_level = profile.difficulty_level).count()
        return JsonResponse({'success': topics_count == 10})
    except Exception as e:
        return JsonResponse({'error': str(e)})
    
# in progress...
@login_required
def check_assessment_questions_status(request):
    try:
        chosen_subject = request.user.learningprofile.chosen_subject
        questions = DifficultyQuestions.objects.filter(subject = chosen_subject)
        if questions.exists():
            return JsonResponse({'ready': True})
        else:
            return JsonResponse({'ready': False})
    except Exception as e:
        return JsonResponse({"error": str(e)})
    

class CustomPasswordChangeView(SuccessMessageMixin, PasswordChangeView):
    template_name = 'password_change.html'
    success_url = reverse_lazy('profile_page')
    success_message = "Your password has been changed successfully."