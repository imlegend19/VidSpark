from rest_framework import serializers

from VidSpark.management.models import Speaker, Video


class SpeakerSerializer(serializers.ModelSerializer):
    videos = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='video-detail'
    )

    class Meta:
        model = Speaker
        fields = ["name", "videos"]
        read_only_fields = fields


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["title", "transcript", "speaker", "indexed"]
        read_only_fields = ["indexed"]
