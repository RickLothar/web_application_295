import pytube
import os
import logging
import uuid

high_resolution = False  #True or False
video_path = 'identify/face_recognition/video/'

def download_video_from_YoutubeURL(url, new_file):
	# dowload to local file
	logging.info("=== start to dowload ===")
	video_url = url
	youtube = pytube.YouTube(video_url)
	logging.info("download: %s", youtube.title)
	if high_resolution:
		video = youtube.streams.filter(adaptive=True,file_extension='mp4').first()
	else : 
		video = youtube.streams.filter(progressive=True,file_extension='mp4').first()
	logging.info(video)
	video.download(video_path, filename=new_file)
	logging.info("=== finish dowloading ===")


