import re
import json

import scrapy
from scrapy import Request, Selector
from scrapy.exceptions import DropItem

from estates.common import extract_number, extract_number_str
from estates.items import Estate, Coords


class EstateSpider(scrapy.Spider):
    name = 'dumrealit'
    allowed_domains = ['dumrealit.cz']
    start_urls = ['https://www.dumrealit.cz/nemovitosti/prodej/byt/okres-hlavni-mesto-praha-3100/razeni-nejnovejsi']

    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def get_page_url(self, page):
        return f'https://www.dumrealit.cz/_nemovitosti/more?filter%5Bfunction%5D=1&filter%5Btype%5D=1&filter%5Blocality%5D%5B%5D=okres%3A3100&filter%5Blocality_text%5D%5B%5D=okres%3A+Hlavn%C3%AD+m%C4%9Bsto+Praha&filter%5Bradius%5D=&filter%5Bnumber%5D=&filter%5Bbroker%5D=&filter%5Boffice%5D=&sort=nejnovejsi&page={page}&count=70'

    def parse(self, response):
        for url in response.css('.real-items-list a.item::attr(href)').extract():
            yield Request(response.urljoin(url), callback=self.parse_estate)

        if response.css('.actions a').extract_first():
            yield Request(
                self.get_page_url(2),
                headers= {
                    'Host': 'www.dumrealit.cz',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'TE': 'trailers',
                },
                meta={
                    'page': 2
                },
                callback=self.parse_load_more)

    def parse_load_more(self, response):
        res_obj = json.loads(response.text)
        content_html = Selector(text=res_obj['content']['content'])

        for url in content_html.css('a.item::attr(href)').extract():
            yield Request(response.urljoin(url), callback=self.parse_estate)

        if content_html.css('.actions a').extract_first():
            yield Request(
                self.get_page_url(response.meta['page'] + 1),
                headers= {
                    'Host': 'www.dumrealit.cz',
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0',
                    'Accept': '*/*',
                    'Accept-Language': 'en-US,en;q=0.5',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'X-Requested-With': 'XMLHttpRequest',
                    'Connection': 'keep-alive',
                    'Sec-Fetch-Dest': 'empty',
                    'Sec-Fetch-Mode': 'cors',
                    'Sec-Fetch-Site': 'same-origin',
                    'Pragma': 'no-cache',
                    'Cache-Control': 'no-cache',
                    'TE': 'trailers',
                },
                meta={
                    'page': response.meta['page'] + 1
                },
                callback=self.parse_load_more)

    def parse_estate(self, response):
        ext_id = response.url.split('_')[-1]
        map_link = response.css('a.map::attr(href)').extract_first()

        if not map_link:
            raise DropItem('Estate without location is not interesting')

        coords_arr = map_link.split('q=')[-1].split('%20')
        coords = Coords(
            lon = float(coords_arr[0]),
            lat = float(coords_arr[1])
        )
        price = extract_number(response.css('div.price strong::text').extract_first())
        url = response.url
        area = int(re.search('(\d+) m2', response.css('title::text').extract_first()).group(1))
        address = response.css('.locality::text').extract_first()
        pictures = list(map(lambda p: response.urljoin(p),response.css('.photos .thumbs a::attr(href)').extract()))

        yield Estate(
                    ext_key = ext_id,
                    orig_address = address,
                    coords_lon = coords['lon'],
                    coords_lat = coords['lat'],
                    url = url,
                    price = price,
                    area = area,
                    pictures = pictures
                )