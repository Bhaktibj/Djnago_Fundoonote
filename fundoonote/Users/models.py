from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

# Regex validators
validate_alphanumeric = RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters are allowed.')
validate_alphabetical = RegexValidator('^[a-zA-Z]', 'Only Alphabetical Characters are allowed.')

class  UserProfile(models.Model):
    user = models.CharField(max_length=30)

    def __str__(self):
        return self.user

class Notes(models.Model):
    # title field  contains the validators
    title = models.CharField(max_length=400, validators=[validate_alphanumeric])
    description = models.CharField(max_length=100, validators=[validate_alphabetical])
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    pub_date = models.DateTimeField(auto_now=True)
    remainder = models.DateTimeField(default=None, null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    COLOR_CHOICES = (
        ('R','Red'),
        ('G','Green'),
        ('B','Blue'),
    )
    color = models.CharField(default='Green', max_length=50, blank=True,choices=COLOR_CHOICES, null=True)
    image = models.ImageField(default=None, null=True)
    trash = models.BooleanField(default=False)

    def __str__(self):  # print string Format
        return self.title

""" Label Models"""
class Label(models.Model):
    text = models.CharField(max_length=100, validators=[validate_alphabetical])
    pub_date = models.DateTimeField(auto_now=True)

    def __str__(self): # print string Format
        return  self.text

""" Link Model is stored the all links"""
class Link(models.Model):
    url = models.URLField()

    def __str(self):
        return self.url