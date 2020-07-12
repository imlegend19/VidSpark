from rest_framework import serializers

from drf_user.serializers import UserSerializer
from VidSpark.management.models import Search, Speaker, Video


class SpeakerSerializer(serializers.ModelSerializer):
    videos = serializers.PrimaryKeyRelatedField(
        many=True,
        read_only=True
    )

    class Meta:
        model = Speaker
        fields = ["name", "videos"]
        lookup_field = "video"


class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = ["title", "transcript", "speaker", "indexed"]
        read_only_fields = ["indexed"]


class SearchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Search
        fields = ["query", "requester", "fuzzy"]
