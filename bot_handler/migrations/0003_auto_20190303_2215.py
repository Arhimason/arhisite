# Generated by Django 2.1.5 on 2019-03-03 18:15

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('bot_handler', '0002_auto_20190122_2305'),
    ]

    operations = [
        migrations.AlterField(
            model_name='storagetable',
            name='peer',
            field=models.CharField(max_length=30, null=True),
        ),
        migrations.AlterField(
            model_name='user',
            name='password',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]