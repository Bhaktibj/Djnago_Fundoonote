import jwt
from django.contrib.auth.models import User
from .redis import RedisMethods
OBJECT = RedisMethods()

def app_login_required(function):
    """ This method is give the authorization to another method"""
    def token_verification(varg):
        # get the value of token from cache
        token_val = OBJECT.get_value('token_key')
        decoded_token = jwt.decode(token_val, 'Cypher', algorithms=['HS256'])
        decoded_id = decoded_token.get('username')
        print("user id", decoded_id)
        # validate the decoded_id with User id
        user = User.objects.get(username=decoded_id)
        print("username", user)
        if decoded_id:
            # if decoded id is found
            return function(varg)
        else:
            raise PermissionError
    return token_verification

def app_pk_login_required(function):
    """ This decorator is give the authorization with pk_value function"""
    def token_verification(varg, pk):
        # get the value of token from cache
        token_val = OBJECT.get_value('token_key')
        # decode the token
        decoded_token = jwt.decode(token_val, 'Cypher', algorithms=['HS256'])
        # decoded token with redis cache
        decoded_id = decoded_token.get('username')
        print("decoded_id", decoded_id)
        # validate the decoded id with user_id
        user = User.objects.get(username=decoded_id)
        print("username", user)
        # If decoded_id is true
        if decoded_id:
            return function(varg, pk)
        else:
            raise PermissionError
    return token_verification