from django import forms
from administrator.models import Student
from django.contrib.auth.forms import UserChangeForm
from django.contrib.auth.models import User

class StudentPhotoForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['picture']


class UserUpdateForm(UserChangeForm):
    password = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    password_confirm = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']

    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')

        if password and password != password_confirm:
            raise forms.ValidationError("Passwords do not match.")

        return password_confirm

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data["password"]
        
        if password:
            user.set_password(password)

        if commit:
            user.save()

        return user