import datetime
import os
import concurrent.futures

from django.core.files import File
from pytube import YouTube
from webvtt import Caption, WebVTT, read
from youtube_transcript_api import YouTubeTranscriptApi

import VidSpark.management.models
from VidSpark import ROOT, THREADS, es
from VidSpark.celery import app
from VidSpark.management.utils import get_youtube_vid_id

CACHE = os.path.join(ROOT, ".cache")


def index_transcript(obj):
    body = {
        "video_id": obj.video_id,
        "start"   : obj.start,
        "end"     : obj.end,
        "subtitle": obj.subtitle
    }

    res = es.index(index="vidspark", doc_type="transcript", body=body, id=obj.id)
    return VidSpark.management.models.TranscriptIndex(transcript=obj, index=res["_id"])


@app.task(name="process_transcript")
def process_transcript(path, vid_id):
    vts = VidSpark.management.models.VideoTranscript.objects.filter(video_id=vid_id)
    print("VTS:", vts)

    vt: VidSpark.management.models.VideoTranscript
    for vt in vts:
        try:
            obj = VidSpark.management.models.TranscriptIndex.objects.get(transcript=vt)
            es.delete(index="vidspark", doc_type="transcript", id=obj.index)
        except Exception:
            break

    objs = []
    for subtitle in read(path):
        trans = VidSpark.management.models.VideoTranscript(video_id=vid_id, start=subtitle.start, end=subtitle.end,
                                                           subtitle=subtitle.text)
        trans.save()

        objs.append(trans)

    objects = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        process = {executor.submit(index_transcript, obj): obj for obj in objs}
        for future in concurrent.futures.as_completed(process):
            if future.exception():
                exception = future.exception()
                print(exception)
                os._exit(1)

            objects.append(future.result())

    VidSpark.management.models.TranscriptIndex.objects.bulk_create(objects)
    objects.clear()

    video = VidSpark.management.models.Video.objects.get(pk=vid_id)
    video.indexed = True
    video.save()


@app.task(name="download_video")
def download_video(url, pk):
    path = os.path.join(CACHE, f"{pk}.mp4")

    yt = YouTube(url)
    yt.streams \
        .filter(progressive=True, file_extension="mp4") \
        .order_by("resolution")[-1] \
        .download(output_path=CACHE, filename=str(pk))

    video = File(path)

    try:
        os.remove(path)
    except FileNotFoundError:
        pass

    while True:
        try:
            obj = VidSpark.management.models.Video.objects.get(pk=pk)
            obj.video = video
            obj.save()
            break
        except Exception:
            pass


@app.task(name="video_processing")
def process_video_url(url, pk):
    vid_id = get_youtube_vid_id(url)
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

    if not os.path.isdir(CACHE):
        os.mkdir(CACHE)

    path = os.path.join(CACHE, f"{vid_id}.vtt")
    vtt.save(path)

    transcript = File(open(path, "rb"))
    os.remove(path)

    obj = VidSpark.management.models.Video.objects.get(pk=pk)
    obj.transcript = transcript
    obj.save()
