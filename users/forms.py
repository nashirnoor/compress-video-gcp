# users/forms.py
from django import forms
from .models import User
from google.cloud import ndb
from django.core.exceptions import ValidationError
from django.core.files.images import get_image_dimensions

client = ndb.Client()

class SignupForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    mobile = forms.CharField(max_length=15)

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

class LoginForm(forms.Form):
    email = forms.EmailField()


class VideoUploadForm(forms.Form):
    video = forms.FileField()  
    def clean_video(self):
        video = self.cleaned_data.get('video')
        return video