from django.shortcuts import render
from .assessment_data import ASSESSMENT_QUESTIONS
from .forms import LearningStyleAssessmentForm


# user_answers = [
#     {'question_id': 1, 'selected_option': 0},  # First option (reading, 3 points)
#     {'question_id': 2, 'selected_option': 1},  # Second option (visual, 3 points)  
#     {'question_id': 3, 'selected_option': 2},  # Third option (hands_on, 3 points)
#     {'question_id': 4, 'selected_option': 1},  # Second option (visual, 3 points)
#     {'question_id': 5, 'selected_option': 0}   # First option (reading, 2 points)
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

        else:
            print("Form has errors")
    else:
        print('User is visitng for the first time')

    form = LearningStyleAssessmentForm()


    return render(request, 'assessment.html', {'form': form})


    
def save_learning_style_results (user, scores):
    profile = user.learningprofile
    profile.visual_learning_score = scores['visual']
    profile.hands_on_learning_score = scores['hands-on']
    profile.reading_learning_score = scores['reading']
    profile.save()
    return profile


def generate_difficulty_assessment_questions(subject):
    
    if subject == 'programming':
        prompt = """Generate 5 multiple choice questions to assess programming knowledge.
        Include: basic syntax, data structures, algorithms, debugging, and software design.
        Range from beginner to advanced concepts."""
    
    elif subject == 'music':
        prompt = """Generate 5 multiple choice questions to assess music theory knowledge.
        Include: basic notation, scales, harmony, composition techniques, and music analysis.
        Range from beginner to advanced concepts."""
    
    elif subject == 'art':
        prompt = """Generate 5 multiple choice questions to assess art knowledge.
        Include: art history periods, techniques, color theory, composition, and art analysis.
        Range from beginner to advanced concepts."""
    
    return ai_generate_questions(prompt)

