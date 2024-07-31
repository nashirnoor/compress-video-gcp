# users/views.py
from django.shortcuts import render, redirect
from .forms import SignupForm, LoginForm, VideoUploadForm
from .models import User,Video
import random
import smtplib
import requests
from .forms import SignupForm, LoginForm
from google.cloud import ndb
from google.cloud import storage
from django.conf import settings
from django.http import JsonResponse
from datetime import timedelta
from google.cloud import ndb
from google.cloud import storage
import uuid
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mobile = form.cleaned_data['mobile']

            client = ndb.Client()
            with client.context():
                if User.query(User.email == email).get():
                    form.add_error('email', 'Email is already in use.')
                elif User.query(User.mobile == mobile).get():
                    form.add_error('mobile', 'Mobile number is already in use.')
                else:
                    user = User(
                        name=form.cleaned_data['name'],
                        email=email,
                        mobile=mobile
                    )
                    user.put()
                    return redirect('login')
    else:
        form = SignupForm()

    return render(request, 'signup.html', {'form': form})

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            
            client = ndb.Client()
            with client.context():
                user = User.query(User.email == email).get()
                if user:
                    otp = str(random.randint(100000, 999999))
                    user.otp = otp
                    user.put()
                    smtp_server = 'smtp.gmail.com'
                    smtp_port = 587
                    smtp_username = 'nashirnoor1718@gmail.com'
                    smtp_password = 'ubbf zilw ofvf tspk'
                    message = f'Subject: OTP\n\nYour OTP is {otp}'
                    
                    try:
                        server = smtplib.SMTP(smtp_server, smtp_port)
                        server.starttls()
                        server.login(smtp_username, smtp_password)
                        server.sendmail(smtp_username, user.email, message)
                        server.quit()
                    except Exception as e:
                        form.add_error(None, 'Error sending email: {}'.format(e))
                        return render(request, 'login.html', {'form': form})

                    return redirect('verify', email=email)
                else:
                    form.add_error('email', 'No user found with this email.')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def verify(request, email):
    if request.method == 'POST':
        otp = request.POST.get('otp')
        
        client = ndb.Client()
        with client.context():
            user = User.query(User.email == email).get()
            if user and user.otp == otp:
                return redirect('get_upload_url')
    return render(request, 'verify.html', {'email': email})



@require_http_methods(["GET", "POST"])
def get_upload_url(request):
    if request.method == 'POST':
        client = storage.Client()
        bucket = client.bucket('test-bucket-video-compress-test')
        blob_name = f'uploads/videos/{uuid.uuid4()}.mp4'
        blob = bucket.blob(blob_name)

        url = blob.generate_signed_url(
            version='v4',
            expiration=timedelta(minutes=15),
            method='PUT',
            content_type='video/mp4',
        )

        return JsonResponse({'url': url, 'blob_name': blob_name})
    else:  
        return HttpResponse("This endpoint generates upload URLs. Please use a POST request to get a URL.")

def upload_success(request):
    if request.method == 'POST':
        blob_name = request.POST.get('blob_name')
        
        client = ndb.Client()
        with client.context():
            user = User.get_by_id(request.session['user_id'])
            if user:
                video = Video(
                    user=user.key,
                    video_url=f'https://storage.googleapis.com/test-bucket-video-compress-test/{blob_name}'
                )
                video.put()
        
        return JsonResponse({'success': True})


def compress_video(request):
    if request.method == 'POST':
        video_url = request.POST.get('video_url')
        compute_instance_ip = 'YOUR_COMPUTE_ENGINE_INSTANCE_IP'
        api_url = f'http://{compute_instance_ip}/compress'

        response = requests.post(api_url, data={'video_url': video_url})

        if response.status_code == 200:
            return JsonResponse({'compressed_video_url': response.json().get('compressed_video_url')})
        else:
            return JsonResponse({'error': 'Compression failed'}, status=500)

    return HttpResponse(status=405)
