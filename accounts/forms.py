# accounts/forms.py
from django import forms
from .models import Member, Admin

class MemberForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)  # optional for edit

    class Meta:
        model = Member
        fields = ['username', 'email', 'password', 'first_name', 'last_name', 'age', 'gender', 'height', 'weight']

class AdminForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = Admin
        fields = ['username', 'email', 'password', 'first_name', 'last_name']