import datetime
import os

from django.core.files import File
from webvtt import Caption, WebVTT
from youtube_transcript_api import YouTubeTranscriptApi

from .models import Video
from VidSpark.celery import app
from VidSpark import ROOT


@app.task(name="video_processing")
def process_video_url(vid_id, pk):
    captions = YouTubeTranscriptApi.get_transcript(video_id=vid_id)

    vtt = WebVTT()

    for t in captions:
        start = datetime.timedelta(milliseconds=t["start"] * 1000)
        end = datetime.timedelta(milliseconds=t["duration"] * 1000) + start

        if "." not in str(start):
            start = str(start) + ".000"

        if "." not in str(end):
            end = str(end) + ".000"

        caption = Caption(
            start=str(start),
            end=str(end),
            text=t["text"]
        )

        vtt.captions.append(caption)

    path = os.path.join(ROOT, ".cache")
    if not os.path.isdir(path):
        os.mkdir(path)

    path = os.path.join(path, f"{vid_id}.vtt")
    vtt.save(path)

    transcript = File(open(path, "rb"))

    video = Video.objects.get(pk=pk)
    video.transcript = transcript
    video.save()
