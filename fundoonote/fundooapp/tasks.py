from __future__ import absolute_import, unicode_literals

from self import self

from .models import Notes, Label
from celery import shared_task, app
from itertools import chain


""" The @shared_task decorator returns a proxy that always uses the task instance 
in the current_app: """
@shared_task
def count_notes():         # count the number of notes
    return Notes.objects.count()

@shared_task
def update_notes(notes_id, title,trash, deleted): # rename the title
    note = Notes.objects.get(id=notes_id)
    note.title=title # take title field
    note.trash=trash
    note.deleted=deleted
    note.save()
    return note

@shared_task
def update_label(label_id, text):  # update label
    label = Label.objects.get(id=label_id)
    label.text=text
    label.save()
@shared_task
def get_all_notes_label():
    note = Notes.objects.filter()
    label = Label.objects.filter()
    note_list = sorted(
        chain(note, label),
        key=lambda notes: notes.pub_date, reverse=True)
    return note_list


from .mail_task import Mailer
mail = Mailer()
mail.send_messages(subject='My App account verification',
                   template='fundooapp/hello.html',
                   context={'customer': self},
                   to_emails=['admin@gmail.com'])
