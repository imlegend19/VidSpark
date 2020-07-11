import re
from uuid import uuid4


def get_video_url(obj, filename):
    if obj.id:
        return f"data/videos/{obj.id}.{filename.split('.')[-1]}"
    else:
        return f"data/videos/{uuid4().hex}.{filename.split('.')[-1]}"


def get_transcript_url(obj, filename):
    if obj.id:
        return f"data/transcripts/{obj.id}.{filename.split('.')[-1]}"
    else:
        return f"data/transcripts/{uuid4().hex}.{filename.split('.')[-1]}"


def get_youtube_vid_id(url):
    pattern = re.compile(
        r"^.*(?:(?:youtu\.be\/|v\/|vi\/|u\/\w\/|embed\/)|(?:(?:watch)?\?v(?:i)?=|\&v(?:i)?=))([^#\&\?]*).*")
    matches = re.search(pattern=pattern, string=url)

    try:
        return matches.group(1)
    except Exception:
        return None
