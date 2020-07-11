from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny


class SpeakerListView(ListAPIView):
    from rest_framework.filters import SearchFilter

    from .models import Speaker
    from .serializers import SpeakerSerializer
    from django_filters.rest_framework.backends import DjangoFilterBackend

    serializer_class = SpeakerSerializer
    queryset = Speaker.objects.all()
    permission_classes = (AllowAny,)

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    search_fields = ('id', 'name')
    filter_fields = ('name',)


class SpeakerRetrieveUpdateView(RetrieveUpdateAPIView):
    from .serializers import SpeakerSerializer
    from .models import Speaker
    from rest_framework.permissions import IsAuthenticated

    queryset = Speaker.objects.all()
    serializer_class = SpeakerSerializer
    permission_classes = (IsAuthenticated,)


class SpeakerCreateView(CreateAPIView):
    from .serializers import SpeakerSerializer
    from .models import Speaker
    from rest_framework.permissions import IsAuthenticated

    serializer_class = SpeakerSerializer
    queryset = Speaker.objects.all()
    permission_classes = (IsAuthenticated,)


class VideoListView(ListAPIView):
    from rest_framework.filters import SearchFilter

    from .models import Video
    from .serializers import VideoSerializer
    from django_filters.rest_framework.backends import DjangoFilterBackend

    serializer_class = VideoSerializer
    queryset = Video.objects.prefetch_related('speaker')
    permission_classes = (AllowAny,)

    filter_backends = (SearchFilter, DjangoFilterBackend,)
    search_fields = ('id', 'title', 'speaker')
    filter_fields = ('title', 'speaker')


class VideoRetrieveUpdateView(RetrieveUpdateAPIView):
    from .serializers import VideoSerializer
    from .models import Video
    from rest_framework.permissions import IsAuthenticated

    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    permission_classes = (IsAuthenticated,)


class VideoCreateView(CreateAPIView):
    from .serializers import VideoSerializer
    from .models import Video
    from rest_framework.permissions import IsAuthenticated

    serializer_class = VideoSerializer
    queryset = Video.objects.all()
    permission_classes = (IsAuthenticated,)
