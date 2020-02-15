import csv

"""
Ted Data Format:

[0: 'comments', 1: 'description', 2: 'duration', 3: 'event', 4: 'film_date', 5: 'languages', 
 6: 'main_speaker', 7: 'name', 8: 'num_speaker', 9: 'published_date', 10: 'ratings', 
 11: 'related_talks', 12: 'speaker_occupation', 13: 'tags', 14: 'title', 15: 'url', 16: 'views']

"""

from bs4 import BeautifulSoup
import requests
import youtube_dl


def fetch_playlist(url):
    vid = {}

    source_code = requests.get(url).text
    soup = BeautifulSoup(source_code, 'html.parser')
    domain = 'https://www.youtube.com'

    for link in soup.find_all("a", {"dir": "ltr"}):
        href = link.get('href')
        if href.startswith('/watch?'):
            vid[link.string.strip()] = domain + href

    return vid


if __name__ == '__main__':
    playlists = [
        "https://www.youtube.com/playlist?list=PLaGOzwY0Dq-LDqy61WiaTTEqkpPc4VPgW",
        "https://www.youtube.com/playlist?list=PLPKaZQAWre5ZsnbzjmPWiSdzOXsaGS2rB",
        "https://www.youtube.com/playlist?list=PLQltO7RlbjPJnbfHLsFJWP-DYnWPugUZ7",
        "https://www.youtube.com/playlist?list=PL70DEC2B0568B5469",
        "https://www.youtube.com/playlist?list=PL5lo6g_GZWyzS3KhLvzpx_GlUnqI6FuP6",
        "https://www.youtube.com/playlist?list=PLPKaZQAWre5bWqn0Fmm8v7XjIOcPyXeEz",
        "https://www.youtube.com/playlist?list=PLa0pZP7tVXwYziZHBuDE-tqEbDSlhFV_e",
        "https://www.youtube.com/playlist?list=PLVk3Hvz7onffkvzCv6Fg-gUpWah3G8ZuS",
        "https://www.youtube.com/playlist?list=PLXi1vrQuYVm7aUtpze6NWYwTnUd0HdVYp",
        "https://www.youtube.com/playlist?list=PL5lo6g_GZWywvJJxHhQGPuUAIA4t8oYx0",
        "https://www.youtube.com/playlist?list=PL8D0F38AF8DF6A53A",
        "https://www.youtube.com/playlist?list=PL378Ue1HV8uKigKxYaldy8vYpvFbxNbTn",
        "https://www.youtube.com/playlist?list=PLgWxkijTb7OpzIVEBIbafmRZQJMIzESEp",
        "https://www.youtube.com/playlist?list=PLB1E709C7689FE1FF",
        "https://www.youtube.com/playlist?list=PL0nKakcqb4tRMwpoDZOEVyt_p-QZrKIpC",
        "https://www.youtube.com/playlist?list=PLrqIFPVT7JUnKsTLseYnyv55pxkLeXT6z",
        "https://www.youtube.com/playlist?list=PLKhCKmqskFaGh-s91DbPU7ck303Sv_nEK",
        "https://www.youtube.com/playlist?list=PLJicmE8fK0EiFRt1Hm5a_7SJFaikIFW30",
        "https://www.youtube.com/playlist?list=PLbN_n6Yvc1k3CBKhmokbqpmNh85eolDQd",
        "https://www.youtube.com/playlist?list=PLoYfRghEMabYRirPkWEXJKUhpzErP2JQb",
        "https://www.youtube.com/playlist?list=PL-SzgE2wbeHlPTF31GDp66aiIp6qGZ7-b"
    ]

    bb_playlist = [
        "https://www.youtube.com/playlist?list=PLZHQObOWTQDPHP40bzkb0TKLRPwQGAoC-",
        "https://www.youtube.com/playlist?list=PL0-GT3co4r2y2YErbmuJw2L5tW4Ew2O5B",
        "https://www.youtube.com/playlist?list=PL0-GT3co4r2wlh6UHTUeQsrf3mlS2lk6x",
        "https://www.youtube.com/playlist?list=PLwrKKKpUt5VJ2QmCYKjq0xkRJkjFauuCq"
        "https://www.youtube.com/playlist?list=PL_h2yd2CGtBHEKwEH5iqTZH85wLS-eUzv",
        "https://www.youtube.com/playlist?list=PLZHQObOWTQDMXMi3bUMThGdYqos36X_lA"
    ]

    urls = set()
    for i in bb_playlist:
        pl = fetch_playlist(i)
        urls = urls.union(set(pl.values()))

    it = 1

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192'
        }],
        'postprocessor_args': [
            '-ar', '16000'
        ],
        'prefer_ffmpeg': True,
        'keepvideo': False,
        'outtmp1': 'youtube/{:05d}'.format(it)
    }

    urls = list(urls)
    for j in range(len(urls)):
        print("Ongoing audio: ", j+1, "/", len(urls))
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([urls[j]])
            it += 1
