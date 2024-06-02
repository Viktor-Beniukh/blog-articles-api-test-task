from django.core.management.base import BaseCommand
from scrapy.cmdline import execute


class Command(BaseCommand):
    help = "Launching a scraper to collect articles from Hacker News"

    def handle(self, *args, **kwargs):
        execute(["scrapy", "crawl", "stories", "-O", "stories.csv"])
