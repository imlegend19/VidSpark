import csv
import os
import re

LINE_REGEX = re.compile(r"^\d*$")
LINE_TIMESTAMP = re.compile(r"^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$")

SRT_PATH = "../../../data/srt/alv_srt"


def parse_srt(f):
    doc = []
    filename = os.path.basename(f)
    sub_title = [int(filename.split(".")[0])]

    csv_file = open("../../../data/alv.csv", "a")
    writer = csv.writer(csv_file)
    writer.writerow(["ID", "Line", "StartTime", "EndTime", "Message"])

    fp = open(f)

    for line in fp.readlines():
        line = line.strip()
        if line == "":
            doc.append(sub_title)
            sub_title = [int(filename.split(".")[0])]
        elif re.match(LINE_REGEX, line):
            sub_title.append(int(line))
        elif re.match(LINE_TIMESTAMP, line):
            start, end = line.split("-->")
            sub_title.append(start.strip())
            sub_title.append(end.strip())
        else:
            sub_title.append(line)

    fp.close()

    print(f"Dumping to csv for -> {filename}")
    writer.writerows(doc)

    csv_file.close()


if __name__ == '__main__':
    files = sorted(os.listdir(f"{SRT_PATH}"))
    for file in files:
        parse_srt(f"{SRT_PATH}/{file}")
