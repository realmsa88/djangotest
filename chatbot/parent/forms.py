from django import forms
from administrator.models import Student

class StudentPhotoForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['picture']
