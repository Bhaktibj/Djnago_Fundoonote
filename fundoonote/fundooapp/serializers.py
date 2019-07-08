from django.contrib.auth.models import User
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers  # import the serializer
from .models import Notes, Label, UserProfile, AWSModel
from .documents import NotesDocument
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
""" Registration Serializer """
class RegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=30)
    email = serializers.RegexField(regex=r'^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$',
                                   required=True)
    password = serializers.CharField(style={'input_type': 'password'})
    class Meta:
        model = UserProfile
        fields = ('username', 'email', 'password')  # fields of username,email and password

class NotesDocumentSerializer(DocumentSerializer):
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    remainder = serializers.DateField(read_only=True)
    class Meta:
        document = NotesDocument
        fields = ('id', 'title', 'description', 'color','remainder')


class AWSModelSerializer(serializers.ModelSerializer):
    bucket_name = serializers.CharField(max_length=30)
    region = serializers.CharField(max_length=100)

    class Meta:
        model= AWSModel
        fields = ('id','bucket_name','region')

