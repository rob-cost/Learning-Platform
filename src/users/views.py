from django.shortcuts import render
from .assessment_data import ASSESSMENT_QUESTIONS
from .forms import LearningStyleAssessmentForm, SubjectSelectionForm
from .models import LearningProfile



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
            profile.save()

            if created:
                print("User accon created")
            else:
                print("Updated user account with scores")


        else:
            print("Form has errors")
    else:
        print('User is visitng for the first time')

    form = LearningStyleAssessmentForm()
    return render(request, 'assessment.html', {'form': form})

def subject_selection_view(request):
    if request.method == 'POST':
        print('User completed the subject form')

        form = SubjectSelectionForm(request.POST)

        if form.is_valid():
            chosen_subject = form.cleaned_data['chosen_subject']
            print(f'user choose: {chosen_subject}')

            profile, created = LearningProfile.objects.get_or_create(user=request.user)
            profile.chosen_subject = chosen_subject
            profile.save()

            if created:
                print("User profile created")
            else:
                print("User choose subject")
    
    else:
        form = SubjectSelectionForm()

    return render(request, 'subject_selection.html', {'form': form})

# def generate_difficulty_assessment_questions(subject):
    
#     if subject == 'programming':
#         prompt = """Generate 5 multiple choice questions to assess programming knowledge.
#         Include: basic syntax, data structures, algorithms, debugging, and software design.
#         Range from beginner to advanced concepts."""
    
#     elif subject == 'music':
#         prompt = """Generate 5 multiple choice questions to assess music theory knowledge.
#         Include: basic notation, scales, harmony, composition techniques, and music analysis.
#         Range from beginner to advanced concepts."""
    
#     elif subject == 'art':
#         prompt = """Generate 5 multiple choice questions to assess art knowledge.
#         Include: art history periods, techniques, color theory, composition, and art analysis.
#         Range from beginner to advanced concepts."""
    
#     return ai_generate_questions(prompt)

