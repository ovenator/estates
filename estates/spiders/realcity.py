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
    name = 'realcity'
    allowed_domains = ['realcity.cz']
    start_urls = ['https://www.realcity.cz/prodej-bytu/hlavni-mesto-praha-1?list-perPage=100&list-sort=price-asc&sp=%7B%22locality%22%3A%5B1%5D%2C%22withImage%22%3Atrue%2C%22transactionTypes%22%3A%5B%22sale%22%5D%2C%22propertyTypes%22%3A%5B%7B%22propertyType%22%3A%22flat%22%2C%22options%22%3A%7B%22ownership%22%3A%5B%22personal%22%5D%7D%7D%5D%7D']

    rules = [
        Rule(LinkExtractor(allow='/nemovitost/'), callback='parse_item'),
        Rule(LinkExtractor(allow='/prodej\-bytu/hlavni\-mesto\-praha\-1\?list\-page='), follow=True)
    ]


    def parse_item(self, response):
        try:
            price = extract_number(response.css('.price-amount::text').extract_first())

            if not price:
                return

            address = response.css('.address::text').extract_first()
            ext_key = response.url.split('-')[-1]
            area = extract_number(re.search('(\d+)\sm²', response.css('title::text').extract_first()).group(1))
            params = deep_strip(response.css('.description').extract_first())
            seller_ref = None
            pictures = list(map(lambda l: EstatePicture(url=l), response.css('.gallery .thumbs a::attr(href)').extract()))
            outer_space = False
            floor = None
            map_url = response.css('#rc-advertise-map::attr(src)').extract_first()
            coords_lon = None
            coords_lat = None

            try:
                seller_ref = extract_number(re.search('Kódzakázky</span><spanclass="list-group-item-value">(.*?)</span>', params).group(1))
            except Exception:
                pass

            try:
                coords_match = re.search('q=(.*?)%2C%20(.*?)&', map_url)
                coords_lat = float(coords_match.group(1))
                coords_lon = float(coords_match.group(2))
            except Exception:
                coords_lon = None
                coords_lat = None
                pass

            try:
                floor_str = re.search('Patro</span><spanclass="list\-group\-item\-value">(.*?)</span>', params).group(1)
                if floor_str == 'přízemí':
                    floor = 0
                else:
                    floor = extract_number(floor_str)
            except Exception:
                pass

            if re.search('Plochabalkónu', params):
                outer_space = True


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
                content = response.css('.content p').extract_first(),
                seller_ref = seller_ref
            )

        except Exception:
            write_error()



