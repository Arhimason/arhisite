# Generated by Django 2.1.5 on 2019-01-22 18:52

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='UserAllInf',
            fields=[
                ('LOG', models.TextField(blank=True)),
                ('id', models.CharField(max_length=20, primary_key=True, serialize=False)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('group', models.CharField(default='None', max_length=20)),
                ('status', models.CharField(blank=True, max_length=150)),
                ('status_audio', models.CharField(blank=True, max_length=100)),
                ('deactivated', models.CharField(blank=True, max_length=10)),
                ('bdate', models.CharField(blank=True, max_length=50)),
                ('city', models.CharField(blank=True, max_length=50)),
                ('country', models.CharField(blank=True, max_length=50)),
                ('home_town', models.CharField(blank=True, max_length=50)),
                ('home_phone', models.CharField(blank=True, max_length=30)),
                ('mobile_phone', models.CharField(blank=True, max_length=30)),
                ('skype', models.CharField(blank=True, max_length=30)),
                ('facebook', models.CharField(blank=True, max_length=30)),
                ('facebook_name', models.CharField(blank=True, max_length=30)),
                ('twitter', models.CharField(blank=True, max_length=30)),
                ('livejournal', models.CharField(blank=True, max_length=30)),
                ('instagram', models.CharField(blank=True, max_length=30)),
                ('site', models.CharField(blank=True, max_length=200)),
                ('nickname', models.CharField(blank=True, max_length=50)),
                ('domain', models.CharField(blank=True, max_length=50)),
                ('relatives', models.CharField(blank=True, max_length=300)),
                ('relation', models.CharField(blank=True, max_length=3)),
                ('relation_partner', models.CharField(blank=True, max_length=100)),
                ('connections', models.CharField(blank=True, max_length=300)),
                ('personal', models.CharField(blank=True, max_length=200)),
                ('activities', models.TextField(blank=True)),
                ('interests', models.TextField(blank=True)),
                ('music', models.TextField(blank=True)),
                ('movies', models.TextField(blank=True)),
                ('tv', models.TextField(blank=True)),
                ('books', models.TextField(blank=True)),
                ('games', models.TextField(blank=True)),
                ('about', models.TextField(blank=True)),
                ('quotes', models.TextField(blank=True)),
                ('universities', models.TextField(blank=True)),
                ('schools', models.TextField(blank=True)),
                ('add_time', models.DateTimeField(auto_now_add=True)),
                ('LOG_modified_time', models.DateTimeField(null=True)),
            ],
        ),
    ]