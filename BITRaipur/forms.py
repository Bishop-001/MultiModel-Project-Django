from django import forms
from .models import Student, College, Department

MODEL_CHOICES = [
    ('student', 'Student'),
    ('college', 'College'),
    ('department', 'Department'),
]


class ModelSelectionForm(forms.Form):
    models = forms.MultipleChoiceField(
        choices=MODEL_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=True,
    )
