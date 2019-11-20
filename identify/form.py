from django import forms
from django.forms.widgets import TextInput
from django.contrib.auth.models import User
from .models import VideoOnline
    
class inputURLForm(forms.Form):
    url = forms.URLField(help_text="https://www.youtube.com/watch?v=JVeJRfLL2sU")
    target = forms.CharField(help_text="Zhu Yilong", required=False)
    making_video = forms.BooleanField(help_text='Explain a little bit', required=False)

class VideoOnlineForm(forms.ModelForm):
    class Meta:
        model = VideoOnline
        fields = ['url']
        labels = {'url':'* YouTube URL'}
    target = forms.CharField(help_text="e.g. Zhu Yilong", required=False)