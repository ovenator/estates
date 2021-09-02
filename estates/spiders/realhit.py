import re
import json

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import DropItem
from scrapy.spiders import Rule,CrawlSpider
from scrapy.linkextractors import LinkExtractor

from estates.common import extract_number, extract_number_str, deep_strip, write_error
from estates.items import Estate, EstatePicture


def last_query(link):
    return link


class EstateSpider(CrawlSpider):
    name = 'realhit'
    allowed_domains = ['volnebytynaprodej.cz']
    start_urls = ['http://www.volnebytynaprodej.cz/?rh_cb_advert_typeid=1&rh_cb_advert_functionid=1&advert_price%5Bfrom%5D=1000000&advert_price%5Bto%5D=&rh_regionid%5B%5D=19&locality_fulltext=&rh_cb_ownershipid%5B%5D=34&floor_area%5Bfrom%5D=&floor_area%5Bto%5D=']

    rules = [
        Rule(LinkExtractor(allow='/detail/'), callback='parse_item'),
        Rule(LinkExtractor(allow='&page=', process_value=last_query), follow=True)
    ]

    # todo fix issue with too long urls
    def parse_item(self, response):
        try:
            ext_key =  response.url.split('/')[-1]
            params = deep_strip(response.css('table.param').extract_first())
            params_with_spaces = response.css('table.param').extract_first()
            area = extract_number(re.search('<th>Podlahováplocha:</th><td>(\d+)m<sup>2</sup></td>', params).group(1))
            price = extract_number(response.css('.price strong::text').extract_first())
            outer_space = None
            address = response.css('table.param tr td[colspan="3"]::text').extract_first()

            if not price:
                return

            try:
                floor = extract_number(re.search('</td><th>Patro:</th><td>(\d+)\.', params).group(1))
            except Exception:
                floor = None

            try:
                re.search('<th>Plochabalkonu:</th><td>(\d+)', params).group(1)
                outer_space = True
            except Exception:
                pass

            try:
                seller_ref = re.search('<th>IDzakázky:</th><td>(.*?)</td>', params).group(1)
            except Exception:
                seller_ref = None
                pass


            pictures = list(map(lambda l: EstatePicture(url=l), response.css('#galerka img[width]::attr(src)').extract()))


            yield Estate(
                ext_key = ext_key,
                orig_address = address,
                coords_lon = None,
                coords_lat = None,
                url = response.url,
                price = price,
                area = area,
                pictures = pictures,
                floor = floor,
                total_floors = None,
                outer_space = outer_space,
                content = response.css('#description').extract_first(),
                seller_ref = seller_ref
            )

        except Exception:
            write_error()



