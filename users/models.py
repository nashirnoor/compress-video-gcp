from django.db import models
from google.cloud import ndb

class User(ndb.Model):
    name = ndb.StringProperty()
    email = ndb.StringProperty()
    mobile = ndb.StringProperty()
    otp = ndb.StringProperty()

class Video(ndb.Model):
    user = ndb.KeyProperty(kind=User)
    video_url = ndb.StringProperty()  
    upload_date = ndb.DateTimeProperty(auto_now_add=True)