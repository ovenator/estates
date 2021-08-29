import os
import re
import json
import traceback

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import DropItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor

from estates.common import extract_number, extract_number_str, strip, write_error, deep_strip
from estates.items import Estate, Coords, EstatePicture


ages = {
    'day': 'https://reality.idnes.cz/s/prodej/byty/cena-nad-1000000/praha/?s-qc%5Bownership%5D%5B0%5D=personal&s-qc%5BarticleAge%5D=1',
    'all': 'https://reality.idnes.cz/s/prodej/byty/cena-nad-1000000/praha/?s-qc[ownership][0]=personal'
}

start_url = ages[os.environ.get('ESTATE_AGE', 'day')]


class EstateSpider(CrawlSpider):
    name = 'idnes'
    allowed_domains = ['reality.idnes.cz']
    start_urls = [start_url]

    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    rules = [
        Rule(LinkExtractor(allow='/detail/prodej/'), callback='parse_item'),
        Rule(LinkExtractor(allow='/s/prodej/.*?&page='), follow=True)
    ]


    def parse_item(self, response):
        try:
            address = strip(response.css('.b-detail__info::text').extract_first())
            pictures = list(map(lambda l: EstatePicture(url=l), response.css('.b-gallery__img-lg .carousel__list a::attr(href)').extract()))
            price = extract_number(response.css('.b-detail__price strong::text').extract_first())
            ext_key = response.url.split('/')[-2]

            area = None
            floor = None
            total_floors = None
            coords_lon = None
            coords_lat = None
            geo_obj = response.css('script[data-maptiler-json]::text').extract_first()
            params = deep_strip(response.css('.b-definition-columns').extract_first())
            seller_ref = None

            if geo_obj:
                feature = json.loads(geo_obj)['geojson']['features'][0]
                coords = feature['geometry']['coordinates']
                coords_lon = coords[0]
                coords_lat = coords[1]

            try:
                floor = extract_number(re.search('(\d+)\. patro', response.css('.b-definition-columns').extract_first()).group(1))
            except Exception:
                pass

            try:
                total_floors = extract_number(re.search('(\d+) podlaží', response.css('.b-definition-columns').extract_first()).group(1))
            except Exception:
                pass

            try:
                area = extract_number(re.search('(\d+)\sm²', response.css('.b-detail__title span::text').extract_first()).group(1))
            except Exception:
                pass

            try:
                seller_ref = re.search('<dt>Číslozakázky</dt><dd>IDNES-(.*?)</dd>', params).group(1)
            except Exception:
                pass

            outer_space = bool(re.search('Terasa|Balkon|Lodžie', response.css('.b-definition-columns').extract_first()))

            yield Estate(
                ext_key = ext_key,
                orig_address = address,
                url = response.url,
                price = price,
                area = area,
                pictures = pictures,
                floor = floor,
                total_floors = total_floors,
                outer_space = outer_space,
                content = response.css('.b-desc').extract_first(),
                coords_lon = coords_lon,
                coords_lat = coords_lat,
                seller_ref = seller_ref
            )
        except Exception as e:
            write_error()

