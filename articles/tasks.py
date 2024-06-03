import csv
import os
import logging

from celery import shared_task
from scrapy.cmdline import execute

from articles.models import Article

logger = logging.getLogger(__name__)

SHARED_DATA_PATH = "/code/shared-data"


@shared_task
def scrape_articles_task():
    output_file = os.path.join(SHARED_DATA_PATH, "stories.csv")
    execute(["scrapy", "crawl", "stories", "-O", output_file])


def _import_articles(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if not Article.objects.filter(scraped_url=row["url"]).exists():
                    Article.objects.create(
                        scraped_title=row["title"],
                        scraped_url=row["url"],
                        source="Scraped"
                    )
        logger.info("Data imported successfully")
    except FileNotFoundError:
        logger.error("File 'stories.csv' not found")


@shared_task
def import_articles_task():
    file_path = os.path.join(SHARED_DATA_PATH, "stories.csv")
    _import_articles(file_path)
