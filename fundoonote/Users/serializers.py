
from django.contrib.auth.models import User
from rest_framework import serializers  # import the serializer
from .models import Notes, Label
""" User Serializer"""
class UserSerializer(serializers.ModelSerializer): # serializer is used to convert the model data into JSON vice versa
    class Meta:
        model = User
        password = serializers.CharField(style={'input_type': 'password'})
        fields = ('url','username','password')

""" Notes Serializer"""
class NotesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notes
        fields = '__all__'

""" label Serializer"""
class LabelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Label
        fields = '__all__'

