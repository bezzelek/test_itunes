import os
import csv
import json

import scrapy

from pathlib import Path
from pandas import read_excel

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.webscraper.items import MusicItem


class ItunesTestSpider(scrapy.Spider):
    name = 'Itunes Test'

    """Preparing files to work with"""
    file_path = Path(__file__).parents[2].joinpath("data_files")
    file_name_xlsx = 'search_input.xlsx'
    file_name_json = 'itunes_test.json'
    file_name_csv = 'itunes_test.csv'
    file_xlsx = Path(file_path).joinpath(file_name_xlsx)
    file_json = Path(file_path).joinpath(file_name_json)
    file_csv = Path(file_path).joinpath(file_name_csv)

    """Extracting input data"""
    search_request_file = read_excel(file_xlsx)
    search_requests = search_request_file.to_dict('records')

    """Updating input data"""
    for item in search_requests:
        item['artist_lower'] = item['Artist name'].lower()
        item['song_lower'] = item['Song title'].lower()

    for item in search_requests:
        artist_name = item['artist_lower'].replace(" ", "+")
        song_name = item['song_lower'].replace(" ", "+")
        item['url_format'] = artist_name + '+' + song_name

    """Getting start urls"""
    start_urls = []
    for item in search_requests:
        element = f'https://itunes.apple.com/search?entity=song&term={item["url_format"]}'
        start_urls.append(element)

    """Spider settings"""
    custom_settings = {
        'FEEDS': {
            file_json: {'format': 'json'}
        },

        'CONCURRENT_REQUESTS': 2,
        'DOWNLOAD_DELAY': 3,
    }

    def parse(self, response, **kwargs):
        """Saving API response"""
        api_response = json.loads(response.text)
        api_results = api_response['results']

        """Defining what is our current request"""
        artist = ''
        song = ''
        for item in self.search_requests:
            if item['url_format'] in response.url:
                artist = item['artist_lower']
                song = item['song_lower']

        """Verifying response and extracting albums that matches our parameter"""
        results_raw = []
        for item in api_results:
            if item['artistName'].lower() == artist and item['trackName'].lower() == song:
                album_id = item["collectionId"]
                album_title = item["collectionName"]
                artist_title = item["artistName"]
                song_title = item['trackName']
                res = {'artist': artist_title, 'album': album_title, 'album_id': album_id, 'song': song_title}
                results_raw.append(res)

        """Removing albums duplicates"""
        results = []
        for item in range(len(results_raw)):
            if results_raw[item] not in results_raw[item + 1:]:
                results.append(results_raw[item])

        """Preparing data for next reauest"""
        for item in results:
            item['album_url_form'] = item['album'].replace("-", "+")
            item['album_url_form'] = item['album'].replace(" ", "+")

        for item in results:
            url = item["album_url_form"]
            item['next_page'] = f'https://itunes.apple.com/search?term={url}&attribute=albumTerm&entity=song&limit=200'

        """Searching albums by title"""
        for item in results:
            next_url = item['next_page']
            yield response.follow(next_url, callback=self.parse_content, meta={'current_data': item})

        """Searching albums by ID"""
        for item in results:
            next_page = f'https://itunes.apple.com/lookup?id={item["album_id"]}&entity=song&limit=200'
            yield response.follow(next_page, callback=self.parse_content, meta={'current_data': item})

    def parse_content(self, response):
        """Saving API response"""
        m_items = MusicItem()
        current_data = response.meta['current_data']
        api_response = json.loads(response.text)
        api_results = api_response['results']

        """Verifying response and extracting songs that matches our parameter"""
        results = []
        for item in api_results:
            try:
                if (item['collectionName'] == current_data['album']) \
                        and (item['collectionId'] == current_data['album_id']) \
                        and (item['kind'] == 'song'):
                    results.append(item)
            except:
                pass

        """Saving raw data"""
        for item in results:
            try:
                m_items['artist_id'] = item['artistId']
                m_items['collection_id'] = item['collectionId']
                m_items['track_id'] = item['trackId']
                m_items['artist_name'] = item['artistName']
                m_items['collection_name'] = item['collectionName']
                m_items['track_name'] = item['trackName']
                m_items['collection_censored_name'] = item['collectionCensoredName']
                m_items['track_censored_name'] = item['trackCensoredName']
                m_items['artist_view_url'] = item['artistViewUrl']
                m_items['collection_view_url'] = item['collectionViewUrl']
                m_items['track_view_url'] = item['trackViewUrl']
                m_items['preview_url'] = item['previewUrl']
                m_items['collection_price'] = item['collectionPrice']
                m_items['track_price'] = item['trackPrice']
                m_items['release_date'] = item['releaseDate']
                m_items['disc_count'] = item['discCount']
                m_items['disc_number'] = item['discNumber']
                m_items['track_count'] = item['trackCount']
                m_items['track_number'] = item['trackNumber']
                m_items['track_time_millis'] = item['trackTimeMillis']
                m_items['country'] = item['country']
                m_items['currency'] = item['currency']
                m_items['primary_genre_name'] = item['primaryGenreName']
            except:
                pass

            yield m_items

    def close(spider, reason):
        """Opening file with raw data"""
        json_data = spider.file_json
        with open(json_data) as file:
            data = json.load(file)
            file.close()
        os.remove(json_data)

        """Removing duplicates"""
        results_data = []
        for item in range(len(data)):
            if data[item] not in data[item + 1:]:
                results_data.append(data[item])
        results_headers = [*results_data[0]]

        """Saving output data"""
        csv_data = spider.file_csv
        try:
            os.remove(csv_data)
            with open(csv_data, 'w') as new_file:
                writer = csv.DictWriter(new_file, fieldnames=results_headers)
                writer.writeheader()
                writer.writerows(results_data)
        except:
            with open(csv_data, 'w') as new_file:
                writer = csv.DictWriter(new_file, fieldnames=results_headers)
                writer.writeheader()
                writer.writerows(results_data)


class ItunesTestScraper:
    def __init__(self):
        settings_file_path = 'webscraper.settings'
        os.environ.setdefault('SCRAPY_SETTINGS_MODULE', settings_file_path)
        self.process = CrawlerProcess(get_project_settings())
        self.spider = ItunesTestSpider

    def run_spiders(self):
        self.process.crawl(self.spider)
        self.process.start()


if __name__ == "__main__":
    scraper = ItunesTestScraper()
    scraper.run_spiders()
