import os

import scrapy

from pathlib import Path
from pandas import read_excel
from w3lib.html import remove_tags

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings


class ChordsTestSpider(scrapy.Spider):
    name = 'Chords Test'

    """Preparing files to work with"""
    file_path = Path(__file__).parents[2].joinpath("data_files")
    file_name_xlsx = 'search_input.xlsx'
    file_xlsx = Path(file_path).joinpath(file_name_xlsx)

    """Extracting input data"""
    search_request_file = read_excel(file_xlsx)
    search_requests = search_request_file.to_dict('records')

    """Updating input data"""
    for item in search_requests:
        item['artist_lower'] = item['Artist name'].lower()
        item['song_lower'] = item['Song title'].lower()

    for item in search_requests:
        artist_name = item['artist_lower'].replace(" ", "%20")
        song_name = item['song_lower'].replace(" ", "%20")
        item['url_format'] = artist_name + '%20' + song_name

    """Getting start urls"""
    start_urls = []
    for item in search_requests:
        element = f'https://www.e-chords.com/search-all/{item["url_format"]}'
        start_urls.append(element)

    """Spider settings"""
    custom_settings = {
        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 1,
        'DOWNLOADER_MIDDLEWARES': {
            'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
            'scrapy_user_agents.middlewares.RandomUserAgentMiddleware': 400,
        },
    }

    def parse(self, response, **kwargs):
        """Defining what is our current request"""
        current_input_data = None
        for item in self.search_requests:
            if item['url_format'] in response.url:
                current_input_data = item

        """Extracting url to content page and following it"""
        results_urls = response.xpath("//div[@class='lista']/div/a[@class='ta']/@href").extract()
        try:
            yield response.follow(
                results_urls[0], callback=self.parse_content, meta={'current_data': current_input_data}
            )
        except:
            pass

    def parse_content(self, response):
        """Extracting page content"""
        current_input_data = response.meta['current_data']
        song_extract = response.xpath('//div[@class="coremain"]').get()
        song = remove_tags(song_extract)

        """Saving content to output file"""
        song_check = len(song)
        if song_check > 0:

            file_name = current_input_data['Artist name'] + ' - ' + current_input_data['Song title'] + '.txt'
            file_txt = Path(self.file_path).joinpath(file_name)
            try:
                os.remove(file_txt)
                with open(file_txt, 'w') as output_file:
                    output_file.write(song)
                    output_file.close()
            except:
                with open(file_txt, 'w') as output_file:
                    output_file.write(song)
                    output_file.close()
        else:
            pass


class ChordsTestScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = ChordsTestSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = ChordsTestScraper()
    scraper.run_spiders()
