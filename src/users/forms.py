from django import forms
from .assessment_data import ASSESSMENT_QUESTIONS
from .models import SUBJECT_CHOICES, LearningProfile
from .ai_question_generator import generate_difficulty_questions

class LearningStyleAssessmentForm (forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for question in ASSESSMENT_QUESTIONS:
            choices= []
            for i, option in enumerate(question['options']):
                choices.append((i, option['text']))

            field_name = f"question_{question['id']}"
            self.fields[field_name] = forms.ChoiceField(
                label=question['question'],
                choices=choices,
                widget=forms.RadioSelect,
                required=True,
                error_messages={'required': f'Please answer question {question["id"]}.'}
            )

    def get_user_answers(self):
        if not self.is_valid():
            return None
        
        user_answers = []
        for question in ASSESSMENT_QUESTIONS:
            field_name =f"question_{question['id']}"
            selected_option = int(self.cleaned_data[field_name])
            
            user_answers.append({
                'question_id': question['id'],
                'selected_option': selected_option
            })
        
        return user_answers
    
class SubjectSelectionForm(forms.Form):
    chosen_subject = forms.ChoiceField(
        label="What would you like to learn?",
        choices=SUBJECT_CHOICES,
        widget=forms.RadioSelect,
        required=True,
        error_messages={'required': 'Please select a subject to continue.'}
    )

class DifficultyAssessmentForm(forms.Form):
    
    def __init__(self, questions_data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        i = 1
    
        for question in questions_data:
            choices = []

            for option_index, option in enumerate(question.answer):
                choices.append((option_index, option))

            field_name = f'question_{i}'
            self.fields[field_name] =  forms.ChoiceField(
                label = question.question,
                choices = choices,
                widget = forms.RadioSelect,
                required = True,
                error_messages={'required': f'Please answer question {field_name}.'}
            )
            self.fields[f'correct_answer_{i}'] = forms.IntegerField(
                widget = forms.HiddenInput(),
                initial = question.correct_answer,
            )
            self.fields[f'points_{i}'] = forms.IntegerField(
                widget = forms.HiddenInput(),
                initial = question.points,
            )


            i+=1


    def get_user_answers_with_correct(self):
        if not self.is_valid():
            return None
        
        score = 0
        max_score = 0
        for i in range(1,6):
            user_answer = int(self.cleaned_data[f'question_{i}'])
            correct_answer = int(self.cleaned_data[f'correct_answer_{i}'])
            points = int(self.cleaned_data[f'points_{i}'])
            max_score += points
            if user_answer  == correct_answer:
                score += points
        
        assessment_score = round((score*100)/max_score)
        return assessment_score


            
            
