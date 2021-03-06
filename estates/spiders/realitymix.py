import re
import json

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import DropItem
from scrapy.spiders import Rule,CrawlSpider
from scrapy.linkextractors import LinkExtractor

from estates.common import extract_number, extract_number_str, deep_strip, write_error
from estates.items import Estate, EstatePicture


class EstateSpider(CrawlSpider):
    name = 'realitymix'
    allowed_domains = ['realitymix.cz']
    start_urls = ['https://realitymix.cz/vyhledavani/praha/prodej-bytu.html']

    rules = [
        Rule(LinkExtractor(allow='/detail/praha/'), callback='parse_item'),
        Rule(LinkExtractor(allow='/vyhledavani/praha/prodej\-bytu\.html\?stranka='), follow=True)
    ]


    def parse_item(self, response):
        try:
            ext_key = extract_number_str(response.url.split('-')[-1])
            orig_address = response.css('.advert-detail-heading__address::text').extract_first()
            url = response.url

            coords_lon = None
            coords_lat = None

            if response.css('#map::attr(data-gps-lon)').extract_first():
                coords_lon = float(response.css('#map::attr(data-gps-lon)').extract_first())
                coords_lat = float(response.css('#map::attr(data-gps-lat)').extract_first())

            price = extract_number(response.css('.advert-detail-heading__price-value::text').extract_first())

            if not price:
                return

            area = extract_number(response.css('.advert-detail-heading__title::text').extract_first().split(',')[-1])
            pictures = list(map(lambda l: EstatePicture(url=l), response.css('.gallery__items img::attr(src)').extract()))

            floor = None
            total_floors = None
            outer_space = False
            seller_data = deep_strip(response.css('.advert-description__short-props').extract_first())
            data = deep_strip(response.css('.detail-information__data-wrapper').extract_first())
            seller_ref = None

            try:
                seller_ref = re.search('<tr><td>????slozak??zky:</td><td>REALITYMIX-(.*?)</td></tr>', seller_data).group(1)
            except Exception:
                pass

            try:
                floor = extract_number(re.search('<span>????slopodla????vdom??:</span><span>(\d+)</span>', data).group(1))
            except Exception:
                pass

            try:
                total_floors = extract_number(re.search('<span>Po??etpodla????objektu:</span><span>(\d+)</span>', data).group(1))
            except Exception:
                pass

            if re.search('<span>Terasa:</span><span>ano</span>', data):
                outer_space = True

            if re.search('<span>Balk??n:</span><span>ano</span>', data):
                outer_space = True

            if re.search('<span>Lod??ie:</span><span>ano</span>', data):
                outer_space = True

            if not re.search('<span>Vlastnictv??:</span><span>osobn??</span>', data):
                return

            yield Estate(
                ext_key = ext_key,
                orig_address = orig_address,
                coords_lon = coords_lon,
                coords_lat = coords_lat,
                url = url,
                price = price,
                area = area,
                pictures = pictures,
                floor = floor,
                total_floors = total_floors,
                outer_space = outer_space,
                content = response.css('.advert-description__text').extract_first(),
                seller_ref = seller_ref
            )

        except Exception:
            write_error()



