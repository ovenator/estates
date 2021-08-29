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
    ext_key = scrapy.Field()
    pictures = scrapy.Field() #Array<EstatePicture>
    floor = scrapy.Field()
    total_floors = scrapy.Field()
    outer_space = scrapy.Field()
    content = scrapy.Field()
    seller_ref = scrapy.Field()

Estate(
    ext_key = None,
    orig_address = None,
    coords_lon = None,
    coords_lat = None,
    url = None,
    price = None,
    area = None,
    pictures = None,
    floor = None,
    total_floors = None,
    outer_space = None,
    content = None,
    seller_ref = None
)