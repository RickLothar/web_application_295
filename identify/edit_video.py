
import logging
import os
from moviepy.editor import VideoFileClip, concatenate_videoclips

input_path = "identify/face_recognition/video/"
generated_path = "identify/static/"

def extract_video_by_target(result, filename, target) :
	logging.info('start to clip video (%s) by target(%s):', filename, target)
	input_video_path = input_path + filename + ".mp4"
	create_directory(filename, target)
	clip = VideoFileClip(input_video_path)
	logging.info("video total length: %s", str(clip.duration))
	total_appear_time = 0
	count = 0;
	for key in result['appearance_time']:
		start_time = key['start_time']
		end_time = key['end_time']
		output_video_path = generated_path + filename + "/" + target+"/" + str(count).zfill(3) + ".mp4"
		logging.info("%s : %s ~ %s",output_video_path,  start_time, end_time)
		new = clip.subclip(start_time, end_time)	
		total_appear_time = total_appear_time + end_time - start_time
		new.write_videofile(output_video_path, audio_codec='aac')
		count+=1
	logging.info('finish clipping')
	logging.info('appear total time : %s', total_appear_time)
	total_appear_time = total_appear_time
	percentage = total_appear_time / clip.duration
	percentage = round(percentage*100, 2)
	logging.info('appear percentage: %s', str(percentage))
	return percentage

def concatenate_video(filename, target) :
	logging.info('start to concatenate video')
	clips = []
	output_video_path = generated_path + filename + "/" + target + "/"
	new_video_name = target + '.mp4'
	dirFiles = os.listdir(output_video_path)
	dirFiles.sort()
	logging.info('dirFiles : %s', dirFiles)
	for file in dirFiles:
		if file.endswith(".mp4"):
			logging.info('concatenate : %s', file)
			clips.append(VideoFileClip(output_video_path+file))

	video = concatenate_videoclips(clips, method='compose')
	video.write_videofile(output_video_path+new_video_name)
	logging.info('finish concatenating : %s', filename + "/" + target + "/" + new_video_name)
	return filename + "/" + target + "/" + new_video_name

def create_directory(filename, target) :
	logging.info('create_directory')
	try:
		path = generated_path + filename
		logging.info('create: %s', path)
		os.mkdir(path)
	except OSError:
		logging.info("Creation of the directory %s failed", path)
	else:
		logging.info("Successfully created the directory %s " % path)
	try:
		path = path +  "/" + target
		logging.info('create: %s', path)
		os.mkdir(path)
	except OSError:
		logging.info("Creation of the directory %s failed" % path)
	else:
		logging.info("Successfully created the directory %s " % path)

