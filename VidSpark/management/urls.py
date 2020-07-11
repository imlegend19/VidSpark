from django.urls import path

from VidSpark.management.views import *

app_name = "management"

urlpatterns = [
    path('video/', VideoListView.as_view(), name="video-list-create"),
    path('video/<int:pk>/', VideoRetrieveUpdateView.as_view(), name="video-retrieve-update-view"),
    path('video/create/', VideoCreateView.as_view(), name="video-create-view"),
    path('speaker/', SpeakerListView.as_view(), name="speaker-list-create"),
    path('speaker/<int:pk>/', SpeakerRetrieveUpdateView.as_view(), name="speaker-retrieve-update-view"),
    path('speaker/create/', SpeakerCreateView.as_view(), name="speaker-create"),
]
