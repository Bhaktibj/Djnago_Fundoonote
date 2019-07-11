from __future__ import absolute_import, unicode_literals
from .models import Notes

from celery import shared_task

@shared_task
def count_notes():
    return Notes.objects.count()

@shared_task
def rename_notes(notes_id, title):
    note = Notes.objects.get(id=notes_id)
    note.title=title
    note.save()


