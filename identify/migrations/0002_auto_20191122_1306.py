# Generated by Django 2.2.7 on 2019-11-22 21:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('identify', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='View',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('type', models.CharField(max_length=200)),
                ('count', models.IntegerField(default=0)),
            ],
        ),
        migrations.AddField(
            model_name='result',
            name='percentage',
            field=models.FloatField(default=0),
        ),
    ]
