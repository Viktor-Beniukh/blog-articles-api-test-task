import os
import csv
from django.core.management.base import BaseCommand
from articles.models import Article


class Command(BaseCommand):
    help = "Import data from CSV file to database"

    def handle(self, *args, **kwargs):
        file_path = os.path.join(os.getcwd(), "stories.csv")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    Article.objects.create(
                        scraped_title=row["title"],
                        scraped_url=row["url"],
                        source="Scraped"
                    )
            self.stdout.write(self.style.SUCCESS("Data imported successfully"))
        except FileNotFoundError:
            self.stdout.write(self.style.WARNING("File 'stories.csv' not found"))
