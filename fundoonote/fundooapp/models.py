from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.auth.models import User  # import USER model
from django.core.validators import RegexValidator   # import regex validator
from django.db.models.signals import post_save

VALIDATE_ALPHANUMERIC = RegexValidator(r'^[a-zA-Z0-9]*$', 'Only alphanumeric characters',                                       'are allowed.')
VALIDATE_ALPHABETIC = RegexValidator(r'^[a-zA-Z]', 'Only Alphabetical Characters are allowed.')
VALIDATE_AWS_REGION = RegexValidator(r'^ap-[a-z]*-[1]{1}$', 'Please follow the region format.')

# this is content type model
class ContentModel(models.Model):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    pub_date = models.DateTimeField()
    class Meta:
        ordering = ['-pub_date']

    def __str__(self):

        return "{0} - {1}".format(self.content_object.text,
                                  self.pub_date.date())
def create_label(sender, instance, created, **kwargs):
    """
    Post save handler to create/update label instances when
     Label is created/updated
    """
    content_type = ContentType.objects.get_for_model(instance)
    try:
        note= ContentModel.objects.get(content_type=content_type,
                             object_id=instance.id)
    except ContentModel.DoesNotExist:
        note = ContentModel(content_type=content_type, object_id=instance.id)
    note.pub_date = instance.pub_date
    note.text = instance.text
    note.created_By = instance.created_By
    note.save()

class Label(models.Model):
    """ This model is used to creating the label"""
    # Use Alphanumeric regex validation
    text = models.CharField(max_length=100, validators=[VALIDATE_ALPHANUMERIC])
    pub_date = models.DateTimeField(auto_now=True)
    created_By = models.ForeignKey(User, related_name='label_created_by', on_delete=models.CASCADE)

    # print text field in string Format.
    def __str__(self):
        return  self.text
print("Label:", Label.__doc__) # print docstring on terminal
post_save.connect(create_label, sender=Label)

class Notes(models.Model):
    """ This model is used to creating the note"""
    # Apply Alphanumerical Regex validators.
    title = models.CharField("Title", max_length=400, validators=[VALIDATE_ALPHANUMERIC])
    # Apply only Alphabetic regex validators.
    description = models.CharField("Description", max_length=100,
                                   validators=[VALIDATE_ALPHABETIC])
    collaborator = models.ManyToManyField(User, related_name='notes')
    pub_date = models.DateTimeField(auto_now=True)
    remainder = models.DateTimeField(default=None, null=True, blank=True)
    is_archive = models.BooleanField(default=False)
    deleted = models.BooleanField(default=False)
    pin = models.BooleanField(default=False)
    # color choice
    COLOR_CHOICES = (
        ('Red', 'Red'),
        ('Ged', 'Green'),
        ('Blue', 'Blue'),
    )
    color = models.CharField(default='Green', max_length=50, blank=True,
                             choices=COLOR_CHOICES, null=True)
    image = models.ImageField(default=None, null=True)
    trash = models.BooleanField(default=False)
    label = models.ForeignKey(Label, related_name='label', on_delete=models.CASCADE)
    created_By = models.ForeignKey(User, related_name='notes_created_by', on_delete=models.CASCADE)

    def __str__(self):
        return "{0} - {1}".format(self.title, self.pub_date)
print("Notes:", Notes.__doc__) # print docstring on terminal

class AWSModel(models.Model):
    """ This Model is used to creating the AWS bucket"""
    bucket_name = models.CharField(max_length=100, unique=True) # bucket name must be unique
    # Apply AWS_Region validators
    region = models.CharField(max_length=100, validators=[VALIDATE_AWS_REGION]) # 'ap-south-1'

    def __str__(self):           # print bucket name in string format
        return self.bucket_name
print("AWSModel:", AWSModel.__doc__) # print docstring on terminal
