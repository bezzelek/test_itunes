import scrapy


class MusicItem(scrapy.Item):
    artist_id = scrapy.Field()
    collection_id = scrapy.Field()
    track_id = scrapy.Field()
    artist_name = scrapy.Field()
    collection_name = scrapy.Field()
    track_name = scrapy.Field()
    collection_censored_name = scrapy.Field()
    track_censored_name = scrapy.Field()
    artist_view_url = scrapy.Field()
    collection_view_url = scrapy.Field()
    track_view_url = scrapy.Field()
    preview_url = scrapy.Field()
    collection_price = scrapy.Field()
    track_price = scrapy.Field()
    release_date = scrapy.Field()
    disc_count = scrapy.Field()
    disc_number = scrapy.Field()
    track_count = scrapy.Field()
    track_number = scrapy.Field()
    track_time_millis = scrapy.Field()
    country = scrapy.Field()
    currency = scrapy.Field()
    primary_genre_name = scrapy.Field()
    pass
