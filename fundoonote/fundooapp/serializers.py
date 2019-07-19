from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django_elasticsearch_dsl_drf.serializers import DocumentSerializer
from rest_framework import serializers  # import the serializer
from .models import Notes, Label, AWSModel
from .documents import NotesDocument
VALIDATE_ALPHANUMERIC = RegexValidator(r'^ap-[a-z]*-[1]{1}$', 'Please follow the region format.')

class RegisterSerializer(serializers.ModelSerializer):
    """This Serializer is used to Register the user through Rest API """
    username = serializers.CharField(max_length=30)
    email = serializers.EmailField(max_length=100)
    password = serializers.CharField(style={'input_type': 'password'})
    class Meta:
        model = User
        fields = ('username', 'email', 'password')  # fields of username,email and password
print("RegisterSerializer:", RegisterSerializer.__doc__)

class LoginSerializer(serializers.ModelSerializer):
    """ This Serializer is used to Login User account"""
    class Meta:
        model = User
        password = serializers.CharField(style={'input_type': 'password'})
        fields = ('username', 'password')
print("LoginSerializer:", LoginSerializer.__doc__)

class UserDetailSerializer(serializers.ModelSerializer):
    """ This serializer is used to display the user detail"""
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'password', 'email')

print("UserDetailSerializer:", UserDetailSerializer.__doc__)

class NotesSerializer(serializers.ModelSerializer):
    """ This serializer is used to serialize the all Notes Model fields"""
    class Meta:
        model = Notes
        fields = '__all__'
print("NotesSerializer:", NotesSerializer.__doc__)

class LabelSerializer(serializers.ModelSerializer):
    """ This serializer is used to serialize the all Label Model fields"""
    class Meta:
        model = Label
        fields = '__all__'
print("LabelSerializer:", LabelSerializer.__doc__)


class NotesDocumentSerializer(DocumentSerializer):
    """ NotesDocument Serializer is serialize the NotesDocument data fields"""
    title = serializers.CharField(read_only=True)
    description = serializers.CharField(read_only=True)
    color = serializers.CharField(read_only=True)
    remainder = serializers.DateField(read_only=True)
    class Meta:
        document = NotesDocument
        fields = ('id', 'title', 'description', 'color', 'remainder')
print("NotesDocumentSerializer:", NotesDocumentSerializer.__doc__)


class AWSModelSerializer(serializers.ModelSerializer):
    """ This Serializer is used to create and delete  bucket"""
    bucket_name = serializers.CharField(max_length=30)
    region = serializers.CharField(max_length=100, validators=[VALIDATE_ALPHANUMERIC])
    class Meta:
        model = AWSModel
        fields = '__all__'
print("AWSModelSerializer:", AWSModelSerializer.__doc__)
