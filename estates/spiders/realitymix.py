import re
import json

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import DropItem

from estates.common import extract_number, extract_number_str
from estates.items import Estate, Coords, EstatePicture


class EstateSpider(scrapy.Spider):
    name = 'realitymix'
    allowed_domains = ['realitymix.cz']
    start_urls = ['https://realitymix.cz/vyhledavani/praha/prodej-bytu.html']

    def get_page_url(self, page):
        return f'https://realitymix.cz/vyhledavani/praha/prodej-bytu.html?stranka={page}'

    def parse(self, response):

        for link in response.css('ul.advert-list-items__items h2 a::attr(href)').extract():
            yield Request(
                link,
                callback=self.parse_estate)

        if not response.css('.paginator .paginator__list-item--disabled .icon-chevron-right').extract_first():
            page = response.meta.get('page', 1)
            next_page = page + 1
            yield Request(
                self.get_page_url(next_page),
                meta={
                    'page': next_page
                },
                callback=self.parse)

    def parse_estate(self, response):
        ext_key = extract_number_str(response.url.split('-')[-1])
        orig_address = response.css('.advert-detail-heading__address::text').extract_first()
        url = response.url

        # todo implement geocoding to make this go away
        if not response.css('#map::attr(data-gps-lon)').extract_first():
            raise DropItem('Missing map, skipping')

        coords = Coords(
            lon = float(response.css('#map::attr(data-gps-lon)').extract_first()),
            lat = float(response.css('#map::attr(data-gps-lat)').extract_first()),
        )

        price = extract_number(response.css('.advert-detail-heading__price-value::text').extract_first())
        area = extract_number(response.css('.advert-detail-heading__title::text').extract_first().split(',')[-1])
        pictures = list(map(lambda l: EstatePicture(url=l), response.css('.gallery__items img::attr(src)').extract()))

        yield Estate(
            ext_key = ext_key,
            orig_address = orig_address,
            coords_lon = coords['lon'],
            coords_lat = coords['lat'],
            url = url,
            price = price,
            area = area,
            pictures = pictures
        )

