# Generated by Django 2.2.4 on 2019-08-23 00:27

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot_handler', '0011_connectedgroup_long_poll_url'),
    ]

    operations = [
        migrations.AlterField(
            model_name='connectedgroup',
            name='access_token',
            field=models.CharField(max_length=128, unique=True),
        ),
    ]
