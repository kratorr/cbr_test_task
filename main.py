import sys
import datetime
import aiohttp
import asyncio

from collections import defaultdict

import xml.etree.ElementTree as ET


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
    try:
        async with session.get(url) as resp:
            assert resp.status == 200
            return await resp.text()
    except aiohttp.ClientConnectorError as e:
        print('Connection Error', str(e))
        sys.exit(1)


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
        nominal = child.find('Nominal').text
        results.append((char_code, name, date, float(value), int(nominal)))
    return results


def get_min_currency(currencies_set):
    min_currency = min(currencies_set, key=lambda i: i[3])
    return min_currency


def get_max_currency(currencies_set):
    max_currency = max(currencies_set, key=lambda i: i[3])
    return max_currency


def get_avg_rouble_currencies(currencies_dict):
    sorted_currency_keys = sorted(
        currencies_dict.keys(), key=lambda key: key[0]
    )
    avg_rouble_currencies = []
    for currency in sorted_currency_keys:
        days = len(currencies_dict[currency])
        avg_rouble_currencies.append(
            [
                currency[1],
                1 / (sum(item[1] for item in currencies_dict[currency]) / days)
            ]
        )
    return avg_rouble_currencies


def parse_currencies(currencies_raw_data: list) -> tuple[set, dict]:
    currencies_dict = defaultdict(list)
    currencies_set = set()
    for currency_raw in currencies_raw_data:
        currency_values = parse_xml(currency_raw)
        for item in currency_values:
            code, name, date, value, nominal = item
            value = value / nominal  # приводим к общему номиналу
            currencies_set.add((code, name, date, value))
            currencies_dict[(code, name)].append((date, value))

    return currencies_set, currencies_dict


def main():
    date_list = get_date_range(DAYS)
    urls = format_urls(date_list)

    currencies_raw_data = asyncio.run(fetch_currency(urls))

    currencies_set, currencies_dict = parse_currencies(currencies_raw_data)
    max_currency_tuple = get_max_currency(currencies_set)
    min_currency_tuple = get_min_currency(currencies_set)

    print(
        f'Минимальный курс валюты:\n'
        f'\t{min_currency_tuple[1]} {min_currency_tuple[3]:.4f} '
        f'{min_currency_tuple[2]}\n'
        f'Максимальный курс валюты:\n'
        f'\t{max_currency_tuple[1]} {max_currency_tuple[3]:.4f} '
        f'{max_currency_tuple[2]}'
    )

    avg_rouble_currencies = get_avg_rouble_currencies(currencies_dict)
    print('Среднее значение рубля по валютам: ')
    for avg_currency in avg_rouble_currencies:
        print(f'\t{avg_currency[0]}: {avg_currency[1]:.4f}')


if __name__ == '__main__':
    main()
