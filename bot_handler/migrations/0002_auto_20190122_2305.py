# Generated by Django 2.1.5 on 2019-01-22 19:05

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('bot_handler', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='storagetable',
            unique_together=set(),
        ),
    ]
