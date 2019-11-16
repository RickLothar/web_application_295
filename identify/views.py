from django.shortcuts import render
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
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
import uuid
import logging
import json
import datetime
from .form import inputURLForm
from .models import Result
from .identify_video_from_url import identify, getTarget_fromResult, getAll_fromResult
from .edit_video import extract_video_by_target, concatenate_video

@login_required
def inputURL(request):

	# If this is a POST request then process the Form data
	if request.method == 'POST':

		if request.user.is_authenticated:
			username = request.user.username
			logging.info('username: %s', username)

		# Create a form instance and populate it with data from the request (binding):
		form = inputURLForm(request.POST)
		if form.is_valid():
			url = form.cleaned_data['url']
			target = form.cleaned_data['target']
			making_video = form.cleaned_data['making_video']

		logging.info('url: %s', url)
		logging.info('target: %s', target)
		filename = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
		logging.info('newfile: %s', filename)
		resultjson = identify(username, str(url), filename,  str(target))
		logging.info('result: %s', resultjson)
		
		# result_obj = Result.objects.get(file_name=filename)
		# resultjson = result_obj.target_result
		# filename = '2019-11-15-19-43-27.mp4'
		output_filepath = ''

		if not target:
			result = getAll_fromResult(resultjson)
			output_filepath = ''
		else:
			result = getTarget_fromResult(resultjson, target)
			if making_video and result['appearance_time']: 
				a = datetime.datetime.now()
				extract_video_by_target(result, filename, target)
				output_filepath = concatenate_video(filename, target)
				b = datetime.datetime.now()
				logging.info("making new video time: %s", str(b-a))
			
		context = {
			'target' : target,
			'result': result,
			'output_filepath': output_filepath
		}

		return render(request, 'result.html', context)

	# If this is a GET (or any other method) create the default form.
	else:
		form = inputURLForm()
		context = {
			'form': form,
		}
		return render(request, 'inputURL.html', context)

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
