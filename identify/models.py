from django.db import models
import uuid
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User


class Channel(models.Model):
    title = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class VideoOnline(models.Model):
    title = models.CharField(max_length=255)
    url = models.URLField()
    youtube_id = models.CharField(max_length=255)
    channel = models.ForeignKey(Channel, on_delete=models.CASCADE)
    def __str__(self):
        return self.title

class View(models.Model):
	type = models.CharField(max_length=200)
	count = models.IntegerField(default=0)


class Result(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular result')
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    videoonline = models.ForeignKey('VideoOnline', on_delete=models.SET_NULL, null=True)
    video =  models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, related_name='input_video')
    output =  models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, related_name='output_video')
    target_name = models.CharField(max_length=200)
    target_result = models.CharField(max_length=200)
    percentage = models.FloatField(default=0)
    length = models.FloatField(default=0)
    def __str__(self):
        return f'{self.id}'
    def get_absolute_url(self):
        return reverse('result-detail', args=[str(self.id)])

class Video(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular video')
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.id}'
    def get_absolute_url(self):
        return reverse('video-detail', args=[str(self.id)])