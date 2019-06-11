from django import forms

from django.contrib.auth.models import User

from .models import Notes, Labels

class UserForm(forms.ModelForm): # UserForm is created the form
    first_name = forms.CharField(max_length=100)
    last_name = forms.CharField(max_length=100)
    password = forms.CharField(widget=forms.PasswordInput())
    email = forms.EmailField(max_length=200)
    class Meta:
        model = User
        fields = ('id','username','first_name','last_name','password', 'email')

class NotesForm(forms.ModelForm): # note form to create the notes
    class Meta:
        model = Notes
        fields = ['title', 'author'] # add 'image'

class LabelsForm(forms.ModelForm):  #create the labels
    class Meta:
        model = Labels
        fields = ('text',)
