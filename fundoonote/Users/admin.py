from django.contrib import admin
from .models import Notes, Label, UserProfile
admin.site.register(Notes)
admin.site.register(Label)
admin.site.register(UserProfile)
