import json
import re
import scrapy
from scrapy.cmdline import execute


class QuotesSpider(scrapy.Spider):

    with open("../../../ted/bus_name.json", 'r') as file:
        data = json.load(file)

    url_auth = {}
    for i in data:
        url_auth[i["video_name"]] = i["speaker"]

    start_urls = []
    for each in data:
        start_urls.append("https://www.ted.com" + str(each['video_name']))

    name = "number"

    def parse(self, response):
        a = response.css("div.main.talks-main")
        x = a.css("script").get()
        regex = r"'(\d+)'"
        regex = re.compile(regex)
        num = re.findall(regex, x)
        num = "".join(num)

        url = response.url.replace("https://www.ted.com", "")

        yield {'id': int(num),
               'video_name': url,
               'speaker': QuotesSpider.url_auth[url]}


execute("scrapy crawl number -o ../../../ted/bus_id.json".split())
