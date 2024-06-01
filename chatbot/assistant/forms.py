# myapp/forms.py

from django import forms

class UserInputForm(forms.Form):
    user_input = forms.CharField(max_length=255)
