from django import forms
from django.contrib.auth.models import User

class UserForm(forms.ModelForm): # UserForm is created the form
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(max_length=200)
    class Meta:
        model = User
        fields = ('username','first_name','last_name','password', 'email')