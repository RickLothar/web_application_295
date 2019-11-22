from django.shortcuts import render, redirect
from django.contrib.auth.decorators import permission_required
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
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
from .form import inputURLForm, VideoOnlineForm
from .models import Result, Channel, Video, VideoOnline
from .identify_video_from_url import inputURL

from django.http import Http404, JsonResponse
from django.forms.utils import ErrorList
from django.views import generic
import urllib
import requests
import threading
from django.core.exceptions import ObjectDoesNotExist

YOUTUBE_API_KEY = 'AIzaSyDuPOQeKiEuzblKFRIOSI2XID9MAkqLiCE'


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

@login_required
def dashboard(request):
    channels = Channel.objects.filter(user=request.user)
    return render(request, 'channels/dashboard.html', {'channels':channels})

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

                # # Take Result output filepath by VideoOnline
                # result = Result.objects.get(videoonline=video)
                # logging.info("view -- result: %s", result.output.file_name)
                return redirect('detail_channel', pk)
            else:
                errors = form._errors.setdefault('url', ErrorList())
                errors.append('Must be a YouTube URL')

    return render(request, 'channels/add_video.html', {'form':form, 'channel':channel})


def inputURLThread(channel, video, target) : 
	# Start to identify face
	inputURL(channel, video, target)
	logging.info('===== channel: %s video: %s target: %s is done ====' , channel.title, video.title, target)


def DetailVideoRender(request, pk):
	videoonline = VideoOnline.objects.get(pk=pk)
	try :
		result = Result.objects.get(videoonline=videoonline)
		clippedvideo = result.output
	except ObjectDoesNotExist:
		clippedvideo = ''
	context = {
		'videoonline':videoonline,
		'clippedvideo':clippedvideo,
		'result':result,
	}

	return render(request, 'channels/detail_video.html', context)

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
