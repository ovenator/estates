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
    name = 'eurobydleni'
    allowed_domains = ['eurobydleni.cz']
    start_urls = ['https://www.eurobydleni.cz/byty/praha/prodej/']

    rules = [
        Rule(LinkExtractor(allow='/detail/'), callback='parse_item'),
        Rule(LinkExtractor(allow='/byty/praha/prodej/page\-'), follow=True)
    ]


    def parse_item(self, response):
        try:
            ext_key = response.url.split('/')[-2]
            params = deep_strip(response.css('.box-params').extract_first())
            address = None
            floor = None
            seller_ref = None
            area = None
            outer_space = False


            if not re.search('<dt>Vlastnictví:</dt><dd>Osobní</dd>', params):
                return

            try:
                price = extract_number(re.search('<dt>Cena:</dt><dd>(\d+)Kč</dd>', params).group(1))
            except Exception:
                return

            area = extract_number(re.search('<dt>Plochaužitná:</dt><dd>(\d+)m<sup>2</sup></dd>', params).group(1))

            try:
                address = re.search('<dt>Adresa:</dt><dd>(.+?)</dd>', params).group(1)
            except Exception:
                pass

            try:
                seller_ref = re.search('<dt>Evidenčníčíslo:</dt><dd>(.*?)</dd>', params).group(1)
            except Exception:
                pass

            try:
                floor = extract_number(re.search('<dt>Patro,podlaží:</dt><dd>(\d+)\.patro</dd>', params).group(1))
            except Exception:
                pass

            if re.search('Terasa|Balkon|Lodžie|Zahrada', params):
                outer_space = True

            coords = response.css(f'#js-page-content [itemid="{response.url}"] [itemprop="geo"] meta::attr(content)').extract()
            coords_lon = float(coords[1])
            coords_lat = float(coords[0])

            pictures = list(map(lambda l: EstatePicture(url='https:' + l), response.css('.detail-img--wrap img::attr(src)').extract()))

            try:
                if re.search('/missing.png',pictures[0]['url']):
                    pictures = []
            except Exception:
                pass

            yield Estate(
                ext_key = ext_key,
                orig_address = address,
                coords_lon = coords_lon,
                coords_lat = coords_lat,
                url = response.url,
                price = price,
                area = area,
                pictures = pictures,
                floor = floor,
                total_floors = None,
                outer_space = outer_space,
                content = response.css('.box-desc').extract_first(),
                seller_ref = seller_ref
            )

        except Exception:
            write_error()



