# Generated by Django 2.1.7 on 2019-06-24 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Users', '0011_auto_20190624_1206'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='user',
        ),
        migrations.AddField(
            model_name='userprofile',
            name='password',
            field=models.CharField(default='', max_length=100),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='userprofile',
            name='username',
            field=models.CharField(default='', max_length=30),
            preserve_default=False,
        ),
    ]
