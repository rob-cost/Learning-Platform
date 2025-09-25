from django import forms
from .assessment_data import ASSESSMENT_QUESTIONS
from .models import SUBJECT_CHOICES 



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
