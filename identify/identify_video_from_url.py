import sys
import logging
import datetime
import uuid
import json
from django.contrib.auth.models import User
from .models import Video, Result
from .face_recognition.download_video import download_video_from_YoutubeURL
from .face_recognition.identify_video import identify_video_main

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', filename='identify/log/web.log',filemode='w')

def identify(username, url, new_file, target_name) :
	file_format = ".mp4"
	download_video_from_YoutubeURL(url, new_file, 0)
	filename = new_file + file_format
	saving_video(username, filename)
	logging.info('video_title: %s', filename)
	result = identify_video_main(filename)

	logging.info('result: %s', result)
	saving_result(username, filename, target_name, result)
	return result

def getTarget_fromResult(resultjson, target_name) :
	result = json.loads(resultjson)
	new_result = {}
	new_result.setdefault('appearance_time',[])
	for key in result['appearance_time']:
		if key['target_name'] == target_name  and key['start_time'] != key['end_time']:
			new_result['appearance_time'].append(key)
	return new_result

def getAll_fromResult(resultjson) :
	return json.loads(resultjson)


def saving_video(username, new_file) :
	logging.info('saving video: %s %s', username, new_file)
	user = User.objects.get(username=username)
	new_video = Video.objects.create(id=uuid.uuid4(), user=user, file_name=new_file)
	new_video.save()

def saving_result(username, file_name, target_name, target_result) :
	logging.info('saving result: %s %s %s %s',username, file_name, target_name, target_result)
	user = User.objects.get(username=username)
	video = Video.objects.get(file_name=file_name)
	target_name = target_name
	target_result = target_result
	new_result = Result.objects.create(id=uuid.uuid4(), user=user, video=video, target_name=target_name, target_result=target_result)
	new_result.save()
