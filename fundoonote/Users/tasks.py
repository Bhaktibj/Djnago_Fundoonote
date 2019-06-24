from __future__ import absolute_import, unicode_literals
from .models import Notes, Label

from celery import shared_task

@shared_task
def count_notes():               # count the number of notes
    return Notes.objects.count()

@shared_task
def update_notes(notes_id, title,trash, deleted):         # rename the title
    note = Notes.objects.get(id=notes_id)
    note.title=title # take title field
    note.trash=trash
    note.deleted=deleted
    note.save()

@shared_task
def update_label(label_id, text):             # update label
    label = Label.objects.get(id=label_id)
    label.text=text
    label.save()
