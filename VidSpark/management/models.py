from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import Signal, receiver
from django.utils.text import gettext_lazy as _
from drfaddons.models import CreateUpdateModel

from VidSpark.management.tasks import process_transcript, process_video_url
from VidSpark.management.utils import get_youtube_vid_id, get_video_url, get_transcript_url

pre_bulk_create = Signal(providing_args=["objs", "batch_size"])
post_bulk_create = Signal(providing_args=["objs", "batch_size"])


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
    video = models.FileField(verbose_name=_("Video"), upload_to=get_video_url, blank=True, null=True)
    video_url = models.CharField(verbose_name=_("Video URL"), max_length=255, blank=True, null=True)
    transcript = models.FileField(verbose_name=_("Transcript"), upload_to=get_transcript_url, blank=True, null=True)
    speaker = models.ForeignKey(verbose_name=_("Speaker"), to=Speaker, on_delete=models.CASCADE)
    indexed = models.BooleanField(verbose_name=_("Indexed"), default=False)

    def save(self, *args, **kwargs):
        if not self.transcript:
            if not self.video_url:
                raise ValidationError(message=_("No transcript, video or video url provided!"))
            else:
                if get_youtube_vid_id(self.video_url):
                    super().save(*args, **kwargs)
                else:
                    raise ValidationError(message=_("Invalid video url"))
        else:
            if self.transcript.name.split(".")[-1] in ["srt", "vtt"]:
                super().save(*args, **kwargs)
            else:
                raise ValidationError(message=_("Invalid transcript file!"))

    def __str__(self):
        return self.title

    class Meta:
        db_table = "videos"
        verbose_name = _("Video")
        verbose_name_plural = _("Videos")


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

    if instance.transcript:
        process_transcript.delay(instance.transcript.path, vid_id)
    else:
        process_video_url.delay(instance.video.url, vid_id)
