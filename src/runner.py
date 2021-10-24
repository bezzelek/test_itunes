import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

from webscraper.spiders.chords_test_spider import ChordsTestSpider
from webscraper.spiders.itunes_test_spider import ItunesTestSpider


def runner():
    settings_file_path = 'webscraper.settings'
    os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)

    process = CrawlerProcess(get_project_settings())

    spider_chords = ChordsTestSpider
    spider_itunes = ItunesTestSpider

    process.crawl(spider_chords)
    process.crawl(spider_itunes)
    process.start()


if __name__ == "__main__":
    runner()
