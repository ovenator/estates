from unittest import TestCase
import re

from estates.common import extract_number


def extract_area(title, desc):
    desc_nosp = re.sub('\s', '', desc)

    area_str = re.search('(\d+)m2', re.sub('\s', '', desc_nosp)).group(1)
    return extract_number(area_str)


class TestEstateSpider(TestCase):

    def test_extract1(self):
        title = 'Byt 1 kk, s predzahradkou.'
        desc = '''V uzavrenem objektu, rekonstrukce provedena italskym architektem Albertem Di Stefano - projekt nazvan Zahrada ruzi.
Byt o vymere 37 m2. Vlastni predzahradka. Dispozicne velmi chytre vyresen, puvodni cihlova klenba zachovana.
Prijemna komunita spolubydlicich, mozno ponechat zarizene. Vice fotek a cely popis na www.bezrealitky.cz

Prima majitelka, prodavam bez realitni kancelare.'''

        area = extract_area(title, desc)
        self.assertEqual(37, area)

