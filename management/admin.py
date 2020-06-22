from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Video)
admin.site.register(VideoSpeaker)
admin.site.register(VideoTranscript)
admin.site.register(Speaker)
