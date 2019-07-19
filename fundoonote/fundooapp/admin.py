from django.contrib import admin
from .models import Notes, Label, AWSModel, ContentModel
admin.site.register(Notes)
admin.site.register(Label)
admin.site.register(AWSModel)
admin.site.register(ContentModel)
