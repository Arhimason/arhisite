# Generated by Django 2.2.4 on 2019-08-23 14:44

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('bot_handler', '0013_auto_20190823_0539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='connectedgroup',
            name='long_poll_url',
        ),
    ]
