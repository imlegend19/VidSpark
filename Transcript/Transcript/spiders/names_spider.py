import scrapy
from scrapy.cmdline import execute


class QuotesSpider(scrapy.Spider):
    page = 1
    name = "names"
    start_urls = ["https://www.ted.com/talks?language=en&page=" + str(page) + "&sort=newest&topics%5B%5D=Business"]

    def parse(self, response):
        count = 0
        for each in response.css("div.talk-link"):
            video_name = each.css("a::attr(href)").get()
            name = each.xpath("//div/h4/text()").getall()[count]
            while name == "\n":
                count += 1
                name = (each.xpath("//div/h4/text()").getall()[count])
            count += 1
            yield {
                'video_name': video_name,
                'speaker': name
            }

            QuotesSpider.page += 1

            if QuotesSpider.page <= 30:
                next_url = "https://www.ted.com/talks?language=en&page=" + str(
                    QuotesSpider.page) + "&sort=newest&topics%5B%5D=Business"
                yield scrapy.Request(next_url, callback=self.parse)


# execute("scrapy crawl names -o ../../../ted/bus_name.json".split())
