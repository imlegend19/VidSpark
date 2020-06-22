import concurrent.futures
import os
from typing import List

import webvtt
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.utils.text import gettext_lazy as _
from drfaddons.models import CreateUpdateModel

from VidSpark import es, THREADS

pre_bulk_create = Signal(providing_args=["objs", "batch_size"])
post_bulk_create = Signal(providing_args=["objs", "batch_size"])
objects = []


class CustomQuerySet(models.QuerySet):
    def bulk_create(self, objs, batch_size=None, **kwargs):
        pre_bulk_create.send(sender=self.model, objs=objs, batch_size=batch_size)
        res = super(CustomQuerySet, self).bulk_create(objs, batch_size)
        post_bulk_create.send(sender=self.model, objs=objs, batch_size=batch_size)
        return res


class Speaker(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        db_table = "speakers"
        verbose_name = "Speaker"
        verbose_name_plural = "Speakers"


class Video(CreateUpdateModel):
    title = models.CharField(verbose_name=_("Title"), max_length=255)
    transcript = models.FileField(verbose_name=_("Transcript"), upload_to="data/")
    indexed = models.BooleanField(verbose_name=_("Indexed"), default=False)

    def save(self, *args, **kwargs):
        if self.transcript.name.split(".")[-1] in ["srt", "vtt"]:
            super().save(*args, **kwargs)
        else:
            raise ValidationError(message=_("Invalid File!"))

    def __str__(self):
        return self.title

    class Meta:
        db_table = "videos"
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")


class VideoSpeaker(models.Model):
    video = models.ForeignKey(verbose_name=_("Video"), to=Video, on_delete=models.CASCADE)
    speaker = models.ForeignKey(verbose_name=_("Speaker"), to=Speaker, on_delete=models.CASCADE)

    def __str__(self):
        return self.video.title

    class Meta:
        db_table = "video_speaker"
        verbose_name = _("Video Speaker")
        verbose_name_plural = _("Video Speakers")


class VideoTranscript(models.Model):
    video = models.ForeignKey(verbose_name=_("Video"), to=Video, on_delete=models.PROTECT)
    start = models.CharField(verbose_name=_("Start Time"), max_length=255)
    end = models.CharField(verbose_name=_("End Time"), max_length=255)
    subtitle = models.TextField(verbose_name=_("Subtitle"))

    objects = CustomQuerySet.as_manager()

    def __str__(self):
        return self.video.title

    class Meta:
        db_table = "transcripts"
        verbose_name = _("Transcript")
        verbose_name_plural = _("Transcripts")


class TranscriptIndex(models.Model):
    transcript = models.ForeignKey(verbose_name=_("Video Transcript"), to=VideoTranscript, on_delete=models.PROTECT)
    index = models.CharField(verbose_name=_("ES Index"), max_length=255)

    def __str__(self):
        return str(self.transcript.video.id) + self.transcript.start + " -> " + self.transcript.end

    class Meta:
        db_table = "transcript_index"
        verbose_name = _("Transcript Index")
        verbose_name_plural = _("Transcript Indexes")


@receiver(signal=post_save, sender=Video)
def process_video(**kwargs):
    instance: Video = kwargs["instance"]
    vid_id = instance.id
    path = instance.transcript.path

    objs = []

    print("Dumping ")

    for subtitle in webvtt.read(path):
        objs.append(VideoTranscript(video_id=vid_id, start=subtitle.start, end=subtitle.end, subtitle=subtitle.text))

    VideoTranscript.objects.bulk_create(objs)
    TranscriptIndex.objects.bulk_create(objects)
    objects.clear()

    print("Dumped Successfully!")


def index_transcript(obj):
    body = {
        "video_id": obj.video_id,
        "start"   : obj.start,
        "end"     : obj.end,
        "subtitle": obj.subtitle
    }

    index = obj.id

    res = es.index(index="vidspark", doc_type="transcript", body=body, id=index)
    objects.append(TranscriptIndex(transcript=obj, index=res["_id"]))
    print(res["_id"])


@receiver(signal=post_bulk_create, sender=VideoTranscript)
def process_transcript(**kwargs):
    objs: List[VideoTranscript] = kwargs["objs"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        process = {executor.submit(index_transcript, obj): obj for obj in objs}
        for future in concurrent.futures.as_completed(process):
            if future.exception():
                exception = future.exception()
                print(exception)
                os._exit(1)
