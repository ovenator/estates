import re
import json
import scrapy

from estates.items import Estate, EstatePicture, Coords


class SrealitySpider(scrapy.Spider):
    name = 'sreality'
    allowed_domains = ['sreality.cz']

    min_items = 0

    min_area = 1
    per_page = 200
    max_price = 100_000_000
    max_age_days=20
    start_urls = [f'https://www.sreality.cz/api/cs/v2/estates?category_main_cb=1&category_type_cb=1&czk_price_summary_order2=100000%7C{max_price}&estate_age={max_age_days}&locality_region_id=10&no_auction=1&ownership=1&per_page={per_page}&tms=1616701027739&usable_area={min_area}%7C10000000000']

    custom_settings = {
        'ROBOTSTXT_OBEY': False
    }

    def parse(self, response):
        res_obj = json.loads(response.text)
        for estate in res_obj['_embedded']['estates']:
            api_url = estate['_links']['self']['href']
            ext_id = api_url.split('/')[-1].split('?')[0]
            address = estate['locality']
            coords = Coords(
                lon = estate['gps']['lon'],
                lat = estate['gps']['lat'],
            )
            price = estate['price']
            try:
                area = re.search('(\d+)\sm²', estate['name']).group(1)
            except Exception as e:
                continue

            pictures = list(map(lambda l: EstatePicture(url=l['href']), estate['_links']['images']))

            yield Estate(
                ext_key = ext_id,
                orig_address = address,
                coords_lon = coords['lon'],
                coords_lat = coords['lat'],
                url = f'https://www.sreality.cz/detail/prodej/hello/world/folks/{ext_id}',
                price = price,
                area = area,
                pictures = pictures
            )
            pass
