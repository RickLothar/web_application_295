from django.db import models
import uuid
from django.urls import reverse # Used to generate URLs by reversing the URL patterns
from django.contrib.auth.models import User


class Result(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular result')
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	video =  models.ForeignKey('Video', on_delete=models.SET_NULL, null=True)
	target_name = models.CharField(max_length=200)
	target_result = models.CharField(max_length=200)
	def __str__(self):
		return f'{self.id}'
	def get_absolute_url(self):
		return reverse('result-detail', args=[str(self.id)])

class Video(models.Model):
	id = models.UUIDField(primary_key=True, default=uuid.uuid4, help_text='Unique ID for this particular video')
	user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
	file_name = models.CharField(max_length=200)
	def __str__(self):
		return f'{self.id}'
	def get_absolute_url(self):
		return reverse('video-detail', args=[str(self.id)])

