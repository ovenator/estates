# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Coords(scrapy.Item):
    lon = scrapy.Field()
    lat = scrapy.Field()

class EstatePicture(scrapy.Item):
    url = scrapy.Field()

class Estate(scrapy.Item):
    area = scrapy.Field()
    price = scrapy.Field()
    url = scrapy.Field()
    orig_address = scrapy.Field()
    coords_lon = scrapy.Field()
    coords_lat = scrapy.Field()
    source_key = scrapy.Field()
    ext_key = scrapy.Field()
    version = scrapy.Field()
    pictures = scrapy.Field() #Array<EstatePicture>