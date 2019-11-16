# Generated by Django 2.2.7 on 2019-11-14 22:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Video',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular video', primary_key=True, serialize=False)),
                ('file_name', models.CharField(max_length=200)),
                ('userid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Result',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, help_text='Unique ID for this particular result', primary_key=True, serialize=False)),
                ('target_name', models.CharField(max_length=200)),
                ('target_result', models.CharField(max_length=200)),
                ('userid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('videoid', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='identify.Video')),
            ],
        ),
    ]
