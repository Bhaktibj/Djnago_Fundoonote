from rest_framework.exceptions import PermissionDenied
from django.http import JsonResponse
import jwt
# View decorators can be used to restrict access to certain views.
def app_login_required(function):
    def wrap(request, *args, **kwargs):
        res = {}
        try:
            token = request.META.get('HTTP_AUTHORIZATION')
            # token = red.get(red, 'token')
            print("Token", token)
            decoded = jwt.decode(token, "secret_key", algorithm='HS256')
            id = decoded.get('id')
            if id:
                return function(request, *args, **kwargs)
            else:
                raise PermissionDenied
        except Exception as e:
            res[ 'message' ] = ' Invalid Token '
            res[ 'success' ] = False
        return JsonResponse(res, status=404)
    # return function(request, *args, **kwargs)
    return wrap