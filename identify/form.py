from django import forms
from django.forms.widgets import TextInput
from django.contrib.auth.models import User
    
class inputURLForm(forms.Form):
    url = forms.URLField(help_text="https://www.youtube.com/watch?v=JVeJRfLL2sU")
    target = forms.CharField(help_text="Yilong Zhu", required=False)
    making_video = forms.BooleanField(required=False)

