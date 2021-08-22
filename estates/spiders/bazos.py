import re
import json

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import DropItem
from scrapy.spiders import Rule, CrawlSpider
from scrapy.linkextractors import LinkExtractor

from estates.common import extract_number, extract_number_str
from estates.items import Estate, Coords, EstatePicture


class EstateSpider(CrawlSpider):
    name = 'bazos'
    allowed_domains = ['reality.bazos.cz']
    start_urls = ['https://reality.bazos.cz/prodam/byt/?hledat=&rubriky=reality&hlokalita=11000&humkreis=20&cenaod=1000000&cenado=5500000&Submit=Hledat&kitx=ano']

    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    rules = [
        Rule(LinkExtractor(allow='/inzerat/'), callback='parse_item'),
        Rule(LinkExtractor(allow='/prodam/byt/.*?/\?hledat'), follow=True)
    ]


    def parse_item(self, response):
        title = response.css('h1.nadpis::text').extract_first()
        desc = ' '.join(response.css('.popisdetail::text').extract())
        pictures = response.css('.carousel-cell-image::attr(data-flickity-lazyload)').extract()
        price_str = response.css('.listadvlevo tr:last-of-type b::text').extract_first()
        price = extract_number(price_str)
        ext_key = re.search('inzerat/(\d+)/', response.url).group(1)

        if not pictures:
            return



        # yield Estate(
        #     ext_key = ext_key,
        #     orig_address = orig_address,
        #     url = response.url,
        #     price = price,
        #     area = area,
        #     pictures = pictures
        # )
        pass