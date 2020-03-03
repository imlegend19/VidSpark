import json
from urllib.request import urlretrieve

if __name__ == '__main__':
    with open("id.json", "r") as fp:
        data = json.load(fp)

    missed = []

    count = 1
    for i in data:
        print("Ongoing", count, "/", len(data))
        url = "https://hls.ted.com/talks/{}/subtitles/en/full.vtt".format(i["id"])
        name = str(i["id"]) + ".vtt"

        try:
            urlretrieve(url, "../dataset/" + name)
        except Exception:
            missed.append(url)

        count += 1

    if missed:
        with open("missed_urls.txt", "w") as fp:
            fp.writelines(missed)
