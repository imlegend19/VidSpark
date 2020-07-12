import re

from drf_yasg.utils import swagger_auto_schema
from rest_framework import pagination, status
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveUpdateAPIView
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from VidSpark import es
from VidSpark.management.serializers import SearchSerializer
from .models import TranscriptIndex


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


def get_filter_query(terms):
    lst = []

    for trm in terms:
        lst.append({
            "term": {
                "subtitle": trm
            }
        })

    return lst


def get_query_result(query: str, fuzzy: bool):
    pattern = re.compile(r'\"(.*?)\"')
    terms = re.findall(pattern, query)

    for term in terms:
        query = query.replace(f'"{term}"', "")

    filter_query = None
    if terms:
        filter_query = get_filter_query(terms)

    if not fuzzy:
        bool_query = {
            "must": [
                {
                    "match": {
                        "subtitle": query
                    }
                }
            ]
        }
    else:
        bool_query = {
            "must": [
                {
                    "match": {
                        "subtitle": {
                            "query"    : query,
                            "fuzziness": "AUTO",
                            "operator":  "and"
                        }
                    }
                }
            ]
        }

    if filter_query:
        bool_query["filter"] = filter_query

    res = es.search(
        index="vidspark",
        body={
            "query": {
                "bool": bool_query
            }
        }
    )

    hits = res["hits"]["total"]["value"]
    final_result = []

    for hit in res["hits"]["hits"]:
        final_result.append({
            "index_id"     : hit["_id"],
            "transcript_id": TranscriptIndex.objects.get(index=hit["_id"]).transcript.pk,
            "score"        : hit["_score"],
            "video"        : hit["_source"]["video_id"],
            "subtitle"     : hit["_source"]["subtitle"],
            "start"        : hit["_source"]["start"],
            "end"          : hit["_source"]["end"]
        })

    return hits, final_result


class CustomPagination(pagination.PageNumberPagination):
    def get_paginated_response(self, data):
        return Response({
            'links'  : {
                'next'    : self.get_next_link(),
                'previous': self.get_previous_link()
            },
            'count'  : self.page.paginator.count,
            'results': data
        })


@swagger_auto_schema(method="POST", request_body=SearchSerializer)
@api_view(["POST"])
def search(request):
    serializer = SearchSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()

        query = serializer.data["query"]
        fuzzy = serializer.data["fuzzy"]

        hits, result = get_query_result(query, fuzzy)

        return Response({
            "hits"   : hits,
            "results": result
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
