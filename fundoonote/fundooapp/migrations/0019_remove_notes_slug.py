# Generated by Django 2.1.7 on 2019-07-05 05:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('fundooapp', '0018_notes_slug'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='notes',
            name='slug',
        ),
    ]
