
from django.contrib.auth.models import User, Group
from rest_framework import serializers # import the serializer

class UserSerializer(serializers.ModelSerializer): # serializer is used to convert the model data into JSON vice versa
    class Meta:
        model = User
        password = serializers.CharField(style={'input_type': 'password'})
        fields = ('url','username','password', 'email', 'first_name','last_name')
