import sys
import logging
import datetime
import uuid
import json
from .models import Video, Result
from .face_recognition.download_video import download_video_from_YoutubeURL
from .face_recognition.identify_video import identify_video_main
from .edit_video import extract_video_by_target, concatenate_video

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s', datefmt='%y-%m-%d %H:%M:%S', filename='identify/log/web.log',filemode='w')

def identify(channel, videoonline, new_file, target_name) :
	url = videoonline.url
	logging.info('url: %s', url)
	logging.info('target: %s', target_name)
	file_format = ".mp4"
	download_video_from_YoutubeURL(url, new_file)
	filename = new_file + file_format
	input_video = saving_video(channel, filename)
	logging.info('video_title: %s', filename)
	result = identify_video_main(filename, target_name)
	result_obj = saving_result(channel, videoonline, input_video, target_name, result)
	logging.info('identify-result: %s', result_obj.target_result)
	return result_obj

def inputURL(channel, videoonline, target):
	filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
	logging.info('newfile: %s', filename)
	result_obj = identify(channel, videoonline, filename,  str(target))
	resultjson = result_obj.target_result
	logging.info('inputURL - result: %s', resultjson)
	result = getTarget_fromResult(resultjson, target)

	if result['appearance_time']: 
		a = datetime.datetime.now()
		percentage = extract_video_by_target(result, filename, target)
		output_filepath = concatenate_video(filename, target)
		output_video = saving_video(channel, output_filepath)
		Result.objects.filter(id=result_obj.id).update(output=output_video, percentage=percentage)
		b = datetime.datetime.now()
		logging.info("making new video time: %s", str(b-a))


def getTarget_fromResult(resultjson, target_name) :
	result = json.loads(resultjson)
	new_result = {}
	new_result.setdefault('appearance_time',[])
	count = 0
	for key in result['appearance_time']:
		if key['target_name'] == target_name  and key['start_time'] != key['end_time']:
			new_result['appearance_time'].append(key)
			count = count+1
	logging.info("Start to clip %s video by result", str(count))
	return new_result

def getAll_fromResult(resultjson) :
	return json.loads(resultjson)


def saving_video(channel, new_file) :
	logging.info('saving video: %s %s', channel, new_file)
	new_video = Video.objects.create(id=uuid.uuid4(), channel=channel, file_name=new_file)
	new_video.save()
	return new_video

def saving_result(channel, videoonline, input_video, target_name, target_result) :
	logging.info('saving result: %s %s %s %s',channel, input_video.file_name, target_name, target_result)
	new_result = Result.objects.create(id=uuid.uuid4(), channel=channel, videoonline=videoonline, video=input_video, target_name=target_name, target_result=target_result)
	new_result.save()
	return  new_result
