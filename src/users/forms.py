from django import forms
from .models import SUBJECT_CHOICES
from django.contrib.auth.models import User

    
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

class ProfileSettingsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']
        widgets = {
            'username': forms.TextInput(attrs:={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs:={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs:={'class': 'form-control'}),
            'email': forms.EmailInput(attrs:={'class': 'form-control'}),
        }
            
            
