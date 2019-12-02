from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import uuid
import logging
import json
import datetime
import time
from .form import inputURLForm, VideoOnlineForm
from .models import Result, Channel, Video, VideoOnline, ViewCount
from .identify_video_from_url import inputURL

from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from django.views import generic
import urllib
import requests
import threading
from django.core.exceptions import ObjectDoesNotExist
from collections import OrderedDict
from django.template.defaulttags import register

YOUTUBE_API_KEY = 'AIzaSyDuPOQeKiEuzblKFRIOSI2XID9MAkqLiCE'

popular_json_path = 'identify/static/popular_celebrity.json'


def userlogin(request):
    if request.method == 'POST':
        form = AuthenticationForm(request=request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            logging.info('username: %s password: %s', username, password)
            if user is not None:
                login(request, user)
                return HttpResponseRedirect(reverse('input_url') )
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    # If this is a GET (or any other method) create the default form.
    else : 
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('home') )
        else:
            form = AuthenticationForm()
            context = {
                'form': form,
            }
            return render(request, 'login.html', context)

def userlogout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home') )

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            form = loginForm()
            context = {
                'form': form,
            }
            return HttpResponseRedirect(reverse('userlogin') )
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})

def history(request):
    if request.user.is_authenticated:
        user = request.user
    history_obj = Result.objects.all().filter(user=user)
    # resultjson = history_obj.target_result
    context = {
        'history': history_obj,
    }
    return render(request, 'history.html', context)

def home(request):
    recent_channels = Channel.objects.all().order_by('-id')[:5]
    # for i in recent_channels:
    #     print(i.id)
    # print(recent_channels)
    # recent_channels = []
    return render(request, 'channels/home.html', {'recent_channels':recent_channels})

@register.filter
def get_item(dictionary, key):
    return dictionary[key]

@login_required
def dashboard(request):
    channels = Channel.objects.filter(user=request.user)
    query_result = Result.objects.filter(channel__in=channels)

    video_result = {}
    for q in query_result:
    	if q.videoonline and q.output :
	    	video_result[q.videoonline.youtube_id] = q.videoonline.title

    return render(request, 'channels/dashboard.html', {'channels':channels, 'results':video_result})

@login_required
def add_video(request, pk):
    form = VideoOnlineForm()
    channel = Channel.objects.get(pk=pk)
    if not channel.user == request.user:
        raise Http404
    if request.method == 'POST':
        form = VideoOnlineForm(request.POST)
        if form.is_valid():
            video = VideoOnline()
            video.channel = channel
            video.url = form.cleaned_data['url']
            target = form.cleaned_data['target']
            parsed_url = urllib.parse.urlparse(video.url)
            video_id = urllib.parse.parse_qs(parsed_url.query).get('v')
            
            if video_id:
                # check if this video is already in the database
                prev_video = VideoOnline.objects.filter(youtube_id=video_id[0])
                if (prev_video.values()):
                    for i in prev_video.values():
                        if pk == i['channel_id']:
                            errors = form._errors.setdefault('url', ErrorList())
                            errors.append('Your channel already inludes this video')
                            return render(request, 'channels/add_video.html', {'form':form, 'channel':channel})

                video.youtube_id = video_id[0]
                response = requests.get(f'https://www.googleapis.com/youtube/v3/videos?part=snippet&id={ video_id[0] }&key={ YOUTUBE_API_KEY }')
                json = response.json()
                title = json['items'][0]['snippet']['title']
                video.title = title
                video.save()

                identify_thread = threading.Thread(target=inputURLThread, args=(channel, video, target))
                identify_thread.start()

                return redirect('detail_channel', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Must be a YouTube URL')

    return render(request, 'channels/add_video.html', {'form':form, 'channel':channel})


def inputURLThread(channel, video, target) : 
	# Start to identify face
	inputURL(channel, video, target)
	logging.info('===== channel: %s video: %s target: %s is done ====' , channel.title, video.title, target)

def trending(request):
	with open(popular_json_path) as json_file:
		data = json.load(json_file)
		popular = {}
		order_popular = {}
		count = 0
		for p in data:
			celebrity = {}
			celebrity['title'] = str(p['celebrity'])
			celebrity['count'] = int(p['number_of_chosen_as_target'])
			popular[count]=celebrity
			count = count+1

		ordered = OrderedDict(sorted(popular.items(), key=lambda i: i[1]['count'], reverse=True))
		order_popular = createNewdic(ordered)
		ordered_json = json.dumps(order_popular)

	videoonline_viewcount_result = ViewCount.objects.filter(videoonline__isnull=False).order_by('-id')
	channel_viewcount_result = ViewCount.objects.filter(channel__isnull=False).order_by('-id')

	recent_channel = channel_viewcount_result[0]
	recent_video = videoonline_viewcount_result[0]
	print(recent_channel)
	print(recent_video)

	videoonline_viewcount = resultTodic(videoonline_viewcount_result)
	channel_viewcount = resultTodic(channel_viewcount_result)

	return render(request, 'trending.html', {'popular':ordered_json, 'videoonline': videoonline_viewcount, 
		'channel':channel_viewcount, 'recent_channel':recent_channel, 'recent_video':recent_video})

def resultTodic(input_result):
	ouput_dic = {}
	count = 0
	for v in input_result: 
		row = {}
		row['title'] = v.title
		row['count'] = v.count
		ouput_dic[count]=row
		count = count+1
	ouput_dic = OrderedDict(sorted(ouput_dic.items(), key=lambda i: i[1]['count'], reverse=True))
	print(ouput_dic)
	ouput_dic = createNewdic(ouput_dic)
	ouput_dic  = json.dumps(ouput_dic)
	return ouput_dic

def createNewdic(old):
	new = {}
	count = 0
	for p in old.items():
		celebrity = {}
		celebrity['title'] = p[1]['title']
		celebrity['count'] = int(p[1]['count'])
		new[count]=celebrity
		count = count+1
		if count == 20:
			break
	return new

def DetailVideoRender(request, pk):
	videoonline = VideoOnline.objects.get(pk=pk)
	addViewCount('', videoonline)
	try :
		result = Result.objects.get(videoonline=videoonline)
		clippedvideo = result.output
		save_times = int(result.length * (100-result.percentage) / 100)
		save_minute = int(save_times/60)
		save_second = save_times - (save_minute*60)

		original_length = convertTime(result.length)
		clipped_length = convertTime(result.length*result.percentage*0.01)

	except ObjectDoesNotExist:
		clippedvideo = ''
		save_minute = 'N/A'
		save_second = 'N/A'
		result =''

	context = {
		'videoonline':videoonline,
		'clippedvideo':clippedvideo,
		'result':result,
		'save_minute':save_minute,
		'save_second':save_second,
		'original_length' :  original_length,
		'clipped_length' :  clipped_length,
	}

	return render(request, 'channels/detail_video.html', context)

def convertTime(second):
	m, s = divmod(second, 60)
	h, m = divmod(m, 60)		
	length = str(int(h)).zfill(2) + ":" + str(int(m)).zfill(2) + ":" + str(int(s)).zfill(2)
	return length

class DetailVideo(generic.DetailView):
    model = VideoOnline
    template_name = 'channels/detail_video.html'

class DeleteVideo(LoginRequiredMixin, generic.DeleteView):
    model = VideoOnline
    template_name = 'channels/delete_video.html'
    # success_url = reverse_lazy('dashboard')

    def get_success_url(self):
        video = super(DeleteVideo, self).get_object()
        channelId = video.channel.id
        return reverse_lazy('detail_channel', args=[channelId])

    def get_object(self):
        video = super(DeleteVideo, self).get_object()
        if not video.channel.user == self.request.user:
            raise Http404
        return video

class SignUp(generic.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy('dashboard')
    template_name = 'registration/signup.html'

    def form_valid(self, form):
        view = super(SignUp, self).form_valid(form)
        # password1 is the password typed in the fields that ask the user to first create a password
        # password2 is the password that asks the user to confirm password
        username, password = form.cleaned_data.get('username'), form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(self.request, user)
        return view


class CreateChannel(LoginRequiredMixin, generic.CreateView):
    model = Channel
    fields = ['title']
    template_name = 'channels/create_channel.html'
    success_url = reverse_lazy('dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        super(CreateChannel, self).form_valid(form)
        return redirect('dashboard')

def DetailChannelRender(request, pk):
	channel = Channel.objects.get(pk=pk)
	query_result = Result.objects.filter(channel=channel)
	video_result = {}
	for q in query_result:
		if q.videoonline and q.output :
			video_result[q.videoonline.youtube_id] = q.videoonline.title
	addViewCount(channel, '')
	return render(request, 'channels/detail_channel.html', {'channel':channel, 'results':video_result})

def getChannelResult(request):
	channel = request.POST.get('post_id')
	query_result = Result.objects.filter(channel=channel)
	video_result = {}
	for q in query_result:
		if q.videoonline and q.output :
			video_result[q.videoonline.youtube_id] = q.videoonline.title

	return HttpResponse(
            json.dumps(video_result),
            content_type="application/json"
    )	

def getDashboardResult(request):
	username = request.POST.get('post_id')
	channels = Channel.objects.filter(user=request.user)
	query_result = Result.objects.filter(channel__in=channels)
	video_result = {}
	for q in query_result:
		if q.videoonline and q.output :
			video_result[q.videoonline.youtube_id] = q.videoonline.title

	return HttpResponse(
            json.dumps(video_result),
            content_type="application/json"
    )

class DetailChannel(generic.DetailView):
    model = Channel
    template_name = 'channels/detail_channel.html'

class UpdateChannel(LoginRequiredMixin, generic.UpdateView):
    model = Channel
    template_name = 'channels/update_channel.html'
    fields = ['title']
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        channel = super(UpdateChannel, self).get_object()
        if not channel.user == self.request.user:
            raise Http404
        return channel

class DeleteChannel(LoginRequiredMixin, generic.DeleteView):
    model = Channel
    template_name = 'channels/delete_channel.html'
    success_url = reverse_lazy('dashboard')

    def get_object(self):
        channel = super(DeleteChannel, self).get_object()
        if not channel.user == self.request.user:
            raise Http404
        return channel

def addViewCount(channel, videoonline) :
	if channel:
		try :
			channel_add = ViewCount.objects.get(channel=channel)
			count = channel_add.count + 1
			ViewCount.objects.filter(channel=channel).update(count=count)
		except ObjectDoesNotExist:
			channel_add = ViewCount.objects.create(channel=channel, count=1, title=channel.title)
			channel_add.save()
		logging.info("channel : %s add one more view count: %d", channel.title, channel_add.count)
		print("channel: " + channel.title + " add one more view count: " + str(channel_add.count))
	if videoonline:
		try :
			video_add = ViewCount.objects.get(videoonline=videoonline)
			count = video_add.count + 1
			ViewCount.objects.filter(videoonline=videoonline).update(count=count)
		except ObjectDoesNotExist:
			video_add = ViewCount.objects.create(videoonline=videoonline, count=1, title=videoonline.title)
			video_add.save()
		logging.info("video : %s add one more view count: %d", videoonline.title, video_add.count)
		print("video: " +videoonline.title + " add one more view count: " + str(video_add.count))


