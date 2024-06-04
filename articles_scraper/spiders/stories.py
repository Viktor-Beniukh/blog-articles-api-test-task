import time
import scrapy
from scrapy.http import Response, HtmlResponse

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


class StoriesSpider(scrapy.Spider):
    name = "stories"
    allowed_domains = ["news.ycombinator.com"]
    start_urls = ["https://news.ycombinator.com/"]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--ignore-certificate-errors")
        self.driver = webdriver.Chrome(options=chrome_options)

    def close(self, reason):
        self.driver.quit()

    @staticmethod
    def parse_page(response: Response):
        for story in response.css(".athing"):
            yield {
                "title": story.css("span.titleline a::text").get(),
                "url": story.css("span.titleline a::attr(href)").get()
            }

    def parse(self, response: Response, **kwargs):
        self.driver.get(response.url)

        while True:
            page_source = self.driver.page_source
            scrapy_response = HtmlResponse(
                url=self.driver.current_url, body=page_source, encoding="utf-8"
            )

            yield from self.parse_page(scrapy_response)

            try:
                more_button = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, ".morelink"))
                )
                self.driver.execute_script("arguments[0].click();", more_button)
                time.sleep(5)
            except Exception as e:
                self.logger.info(f"Error clicking 'More' button: {e}")
                break
