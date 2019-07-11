from django.core.exceptions import PermissionDenied
from .models import Notes
def user_is_note_author(function):
    def wrap(request, *args, **kwargs):
        note = Notes.objects.get(pk=kwargs['pk'])
        if note.created_by == request.user:
            return function(request, *args, **kwargs)
        else:
            raise PermissionDenied
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap