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

class ViewCount(models.Model):
	id = models.AutoField(auto_created=True, primary_key=True)
	title = models.CharField(max_length=255, null=True)
	count = models.IntegerField(default=0)
	videoonline = models.ForeignKey('VideoOnline', on_delete=models.SET_NULL, null=True)
	channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
	def __str__(self):
		return self.title

class Result(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    videoonline = models.ForeignKey('VideoOnline', on_delete=models.SET_NULL, null=True)
    video =  models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, related_name='input_video')
    output =  models.ForeignKey('Video', on_delete=models.SET_NULL, null=True, related_name='output_video')
    target_name = models.CharField(max_length=200)
    target_result = models.TextField()
    percentage = models.FloatField(default=0)
    length = models.FloatField(default=0)
    def __str__(self):
        return f'{self.id}'
    def get_absolute_url(self):
        return reverse('result-detail', args=[str(self.uuid)])

class Video(models.Model):
    id = models.AutoField(auto_created=True, primary_key=True)
    channel = models.ForeignKey(Channel, on_delete=models.SET_NULL, null=True)
    file_name = models.CharField(max_length=200)
    def __str__(self):
        return f'{self.id}'
    def get_absolute_url(self):
        return reverse('video-detail', args=[str(self.uuid)])