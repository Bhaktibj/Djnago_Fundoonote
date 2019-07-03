from django.http import JsonResponse, HttpResponse
from rest_framework.exceptions import PermissionDenied

from .models import User
import jwt
def app_login_required(function):
    def wrap(request, *args, **kwargs):
        res = {}
        try:
            print(request.META.get('HTTP_AUTHORIZATION')) # Header
            token = request.META.get('HTTP_AUTHORIZATION') # Get a Token from a Header
            token_decode = jwt.decode(token, "secret_key", algorithms=['HS256']) # Decode the Token
            eid = token_decode.get('email')     # Additional code of a decorator to get an email
            user_id = User.object.get(email=eid) # Get the User Id
            entry=user_id # Assign the User Id
            request.user_id = user_id # Request the User Id
            if entry: # If User ID
                return function(request, *args, **kwargs)  # Return Outer Function
            else:
                raise PermissionDenied  # Invalid
        except Exception as e: # Raise Exception
            print(e)
            res['message'] = 'Something bad happend'
            return JsonResponse(res, status=404)
    return wrap # Return Inner Function