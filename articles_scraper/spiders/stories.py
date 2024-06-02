import scrapy


class StoriesSpider(scrapy.Spider):
    name = "stories"
    allowed_domains = ["news.ycombinator.com"]
    start_urls = ["https://news.ycombinator.com/"]

    def parse(self, response):
        pass
