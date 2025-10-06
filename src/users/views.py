from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from .assessment_data import ASSESSMENT_QUESTIONS
from .forms import LearningStyleAssessmentForm, SubjectSelectionForm, DifficultyAssessmentForm
from .models import LearningProfile
from .ai_question_generator import generate_difficulty_questions
from lessons.ai_topic_generator import generate_topic



# user_answers = [
#     {'question_id': 1, 'selected_option': 0},  # First option (reading, 3 points)
# ]

user_answers = []

def calculate_learning_score(user_answers):
    scores = {
        'reading' : 0,
        'visual' : 0,
        'hands_on' : 0
    }

    for answer in user_answers:
        question = ASSESSMENT_QUESTIONS[answer['question_id'] -1]
        selected_option = question['options'][answer['selected_option']]

        learning_style = selected_option['learning_style']
        points = selected_option['points']

        scores[learning_style] += points

    return scores
    
def learning_style_assessment_view(request):

    profile = request.user.learningprofile
    if profile.registration_step != 1:
        messages.error(request, "You already completed this step.")
        return redirect('landing')

    if request.method == 'POST':
        print('User submitted the form')

        form = LearningStyleAssessmentForm(request.POST)

        if form.is_valid():
            print("Form is valid")

            user_answers = form.get_user_answers()
            print("user answers: ", user_answers)

            scores = calculate_learning_score(user_answers)
            print("Calculated scores:", scores)

            profile, created = LearningProfile.objects.get_or_create(user=request.user)
            profile.visual_learning_score = scores['visual']
            profile.hands_on_learning_score = scores['hands_on']
            profile.reading_learning_score = scores['reading']
            profile.registration_step = 2
            profile.save()

            if created:
                print("User account created")
            else:
                print("Updated user account with scores")


        else:
            print("Form has errors")

        return redirect('subject_selection') 
    else:
        print('User is visitng for the first time')

    form = LearningStyleAssessmentForm()
    return render(request, 'assessment.html', {'form': form})

def subject_selection_view(request):

    profile = request.user.learningprofile
    if profile.registration_step != 2:
        messages.error(request, "You already completed this step.")
        return redirect('landing')

    if request.method == 'POST':
        print('User completed the subject form')

        form = SubjectSelectionForm(request.POST)

        if form.is_valid():
            chosen_subject = form.cleaned_data['chosen_subject']
            print(f'user choose: {chosen_subject}')

            profile, created = LearningProfile.objects.get_or_create(user=request.user)
            profile.chosen_subject = chosen_subject
            profile.registration_step = 3
            profile.save()

            if created:
                print("User profile created")
            else:
                print("User choose subject")
            return redirect('difficulty_assessment') 
    
    else:
        form = SubjectSelectionForm()

    return render(request, 'subject_selection.html', {'form': form})

def difficulty_assessment_view(request):
    profile = request.user.learningprofile
    chosen_subject = profile.chosen_subject

    if profile.registration_step != 3:
        messages.error(request, "You already completed this step.")
        return redirect('landing')

    if request.method == "POST":
        form = DifficultyAssessmentForm(subject = chosen_subject, data = request.POST)

        if form.is_valid():
            assessment_score = form.get_user_answers_with_correct()
            profile = LearningProfile.objects.get(user = request.user)
            profile.assessment_score = assessment_score
            profile.difficulty_assessment_completed = True
            profile.registration_step = 4
            if assessment_score > 80:
                profile.difficulty_level = 'advanced'
            elif assessment_score >50:
                profile.difficulty_level = 'intermediate'
            else:
                profile.difficulty_level = 'beginner'
            profile.save()

            generate_topic(chosen_subject)

            messages.success(request, "Well done you have completed the registration process!")
            return redirect('profile_page') 

    else:
        form = DifficultyAssessmentForm(subject = chosen_subject)

    return render(request, 'difficulty_assessment.html', {'form': form})

def test_generate_ai_questions(request):
    questions = generate_difficulty_questions('programming')
    return render(request, 'test_questions.html', {'questions': questions})

def signup_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            LearningProfile.objects.create(user = user)
            login(request, user)
            return redirect('learning_style_assessment')
    else: 
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})
        
@login_required
def landing_view(request):
    try:
        profile = request.user.learningprofile
        step = profile.registration_step

        if step == 1:
            return redirect('learning_style_assessment')
        if step == 2:
            return redirect('subject_selection')
        if step == 3:
            return redirect('difficulty_assessment')
        else:
            return redirect('profile_page')
    except LearningProfile.DoesNotExist:
        LearningProfile.objects.create(user = request.user)
        return redirect('learning_style_assessment')

@login_required
def profile_view(request):
    profile = request.user.learningprofile

    context = {
        'profile' : profile,
        'username' : request.user.username
    }

    return render(request, 'profile.html', context)