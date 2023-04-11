import datetime
import aiohttp
import asyncio
import logging
import xml.etree.ElementTree as ET
from collections import defaultdict

#TODO sdelat' logger dla example
logging  = logging.getLogger()


URL = 'http://www.cbr.ru/scripts/XML_daily_eng.asp?date_req={date}'
DAYS = 90


def get_date_range(n=1):
    base = datetime.datetime.today()
    date_list = []
    for day in range(n):
        date_obj = base - datetime.timedelta(days=day)
        date_list.append(date_obj.strftime("%d/%m/%Y"))
    return date_list


async def fetch_currency(urls):
    async with aiohttp.ClientSession() as session:
        coros = [asyncio.create_task(fetch(session, url)) for url in urls]
        return await asyncio.gather(*coros)


async def fetch(session, url):
    async with session.get(url) as resp:
        assert resp.status == 200
        return await resp.text()


def format_urls(date_list):
    return [URL.format(date=date) for date in date_list]


def parse_xml(xml_string):
    results = []

    tree = ET.ElementTree(ET.fromstring(xml_string))
    root = tree.getroot()

    date = root.attrib['Date']
    for child in root:
        char_code = child.find('CharCode').text
        value = child.find('Value').text.replace(',', '.')
        name = child.find('Name').text
        results.append((char_code, name, date, float(value)))
    return results


def parse_currencies(currencies_raw_data):
    currencies_dict = defaultdict(list)

    for currency_raw in currencies_raw_data:
        currency_values = parse_xml(currency_raw)
        for item in currency_values:
            code, name, date, value = item
            currencies_dict[(code, name)].append((date, value))

    return currencies_dict


def get_min_currency(key, currencies_dict):
    min_currency = min(currencies_dict[key], key=lambda i: i[1])
    return min_currency


def get_max_currency(key, currencies_dict):
    max_currency = max(currencies_dict[key], key=lambda i: i[1])
    return max_currency


def get_avg_rouble_currency(currencies_dict):
    denominator_avg = len(currencies_dict) * DAYS

    sum_of_all_currencies = 0

    for currenry_list in currencies_dict.values():
        sum_of_all_currencies += sum(item[1] for item in currenry_list)

    return sum_of_all_currencies / denominator_avg


def main():
    date_list = get_date_range(90)
    urls = format_urls(date_list)

    currencies_raw_data = asyncio.run(fetch_currency(urls))

    currencies_dict = parse_currencies(currencies_raw_data)
    sorted_currency_keys = sorted(
        currencies_dict.keys(), key=lambda key: key[0]
    )
    for currency_key in sorted_currency_keys:
        max_currency_tuple = get_max_currency(currency_key, currencies_dict)
        min_currency_tuple = get_min_currency(currency_key, currencies_dict)
        print(
            f'{currency_key[1]}:\n'
            f'\tMin: {min_currency_tuple[1]} {min_currency_tuple[0]}\n'
            f'\tMax: {max_currency_tuple[1]} {max_currency_tuple[0]}'
        )
    print('')
    avg_rouble_currency = get_avg_rouble_currency(currencies_dict)
    print(
        f'Average rouble currency: {avg_rouble_currency}'
    )


if __name__ == '__main__':
    main()
