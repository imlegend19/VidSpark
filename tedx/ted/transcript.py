import json
from urllib.request import urlretrieve

if __name__ == '__main__':
    with open("bus_id.json", "r") as fp:
        data = json.load(fp)

    missed = []

    count = 1
    for i in data:
        print("Ongoing", count, "/", len(data))
        url = "https://hls.ted.com/talks/{}/subtitles/en/full.vtt".format(i["id"])
        name = str(i["id"]) + ".vtt"

        try:
            urlretrieve(url, "../dataset/business/" + name)
        except Exception:
            missed.append(url)

        count += 1

    if missed:
        with open("bus_vtt_missed_urls.txt", "w") as fp:
            for each in missed:
                fp.writelines(each)
