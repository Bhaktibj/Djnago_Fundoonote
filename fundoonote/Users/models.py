
from django.db import models
# Create your models here.
from django.urls import reverse


class Notes(models.Model):
    title = models.CharField(max_length=400)
    author = models.TextField(max_length=10)
    created_time = models.DateTimeField(auto_now_add=True, null=True)
    # image = models.FileField(upload_to='images/')
    def __str__(self):
        return self.title

    def get_post_url(self):
        return reverse('note_edit', kwargs={'pk': self.pk})

class Labels(models.Model):
    text = models.TextField(max_length=10)
    created_time = models.DateTimeField(auto_now_add=True, null=True)

    def __str__(self):
        return self.text

