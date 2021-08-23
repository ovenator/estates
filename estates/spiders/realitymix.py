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
    start_urls = ['https://realitymix.cz/vypis-nabidek/?form%5Badresa_kraj_id%5D[]=19&form%5Badresa_obec_id%5D=&form%5Bcena_mena%5D=&form%5Bcena_normalizovana__from%5D=1000000&form%5Bcena_normalizovana__to%5D=&form%5Bexclusive%5D=&form%5Bfk_rk%5D=&form%5Binzerat_typ%5D=1&form%5Bnemovitost_typ%5D=4&form%5Bplocha__from%5D=&form%5Bplocha__to%5D=&form%5Bpodlazi_cislo__from%5D=&form%5Bpodlazi_cislo__to%5D=&form%5Bprojekt_id%5D=&form%5Bsearch_in_city%5D=&form%5Bsearch_in_text%5D=&form%5Bstari_inzeratu%5D=&form%5Bstav_objektu%5D=&form%5Btop_nabidky%5D=&form%5Bvlastnictvi%5D[]=1']

    rules = [
        Rule(LinkExtractor(allow='/detail/praha/'), callback='parse_item'),
        Rule(LinkExtractor(allow='/vypis\-nabidek/\?form'), follow=True)
    ]


    def parse_item(self, response):
        try:
            ext_key = extract_number_str(response.url.split('-')[-1])
            orig_address = response.css('.advert-detail-heading__address::text').extract_first()
            url = response.url

            coords_lon = None
            coords_lat = None

            if response.css('#map::attr(data-gps-lon)').extract_first():
                coords_lon = float(response.css('#map::attr(data-gps-lon)').extract_first()),
                coords_lat = float(response.css('#map::attr(data-gps-lat)').extract_first()),

            price = extract_number(response.css('.advert-detail-heading__price-value::text').extract_first())
            area = extract_number(response.css('.advert-detail-heading__title::text').extract_first().split(',')[-1])
            pictures = list(map(lambda l: EstatePicture(url=l), response.css('.gallery__items img::attr(src)').extract()))

            floor = None
            total_floors = None
            outer_space = False
            data = deep_strip(response.css('.detail-information__data-wrapper').extract_first())

            try:
                floor = extract_number(re.search('<span>Číslopodlažívdomě:</span><span>(\d+)</span>', data).group(1))
            except Exception:
                pass

            try:
                total_floors = extract_number(re.search('<span>Početpodlažíobjektu:</span><span>(\d+)</span>', data).group(1))
            except Exception:
                pass

            if re.search('<span>Terasa:</span><span>ano</span>', data):
                outer_space = True

            if re.search('<span>Balkón:</span><span>ano</span>', data):
                outer_space = True

            if re.search('<span>Lodžie:</span><span>ano</span>', data):
                outer_space = True


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
                content = response.css('.advert-description__text').extract_first()
            )

        except Exception:
            write_error()



