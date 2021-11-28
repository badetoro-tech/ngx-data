from bs4 import BeautifulSoup
import requests
from pprint import pprint
import ast
from config import ngx_url, header, debug

NXG_URL = ngx_url
HEADER = header


def extract_equity_info(page_url):
    response = requests.get(page_url, headers=HEADER)
    page_extract = response.text
    soup = BeautifulSoup(page_extract, "html.parser")
    if debug >= 4:  # 4
        print('*** Spooling BeautifulSoup Extract ... *** ')
        print(soup.prettify())

    profile_data = soup.find(name="table", class_="wpDataTable")
    trading_info = profile_data.find_all(name="strong")

    dynamic_string = '{'
    for record in trading_info:
        dynamic_string += "'" + str(record).split("\"")[1] + "': '" + str(record.getText()) + "',"

    profile_data = soup.find(name="div", class_="ngx-tabs")
    profile_title = profile_data.find_all(name="td")

    cnt = 0
    title = ''
    # profile_rec = []
    for record in profile_title:
        # print(str(profile_title.index(record)))
        if cnt % 2 == 0:
            dynamic_string += "'" + (record.getText().strip()).split(':')[0] + "': '" + '' + "',"
        cnt += 1

    dynamic_string += '}'
    data_record = ast.literal_eval(dynamic_string)

    for record in profile_title:
        # print(str(profile_title.index(record)))
        if cnt % 2 == 0:
            title = (record.getText().strip()).split(':')[0]
        else:
            data_record[str(title)] = (record.getText().strip())
        cnt += 1

    return data_record


def extract_bond_info(page_url):
    response = requests.get(page_url, headers=HEADER)
    page_extract = response.text
    soup = BeautifulSoup(page_extract, "html.parser")
    if debug >= 4:  # 4
        print('*** Spooling BeautifulSoup Extract ... *** ')
        print(soup.prettify())

    profile_data = soup.find(name="table", class_="wpDataTable")
    bond_info = profile_data.find_all(name="td")

    if debug >= 4:  # 4
        pprint(bond_info)

    cnt = 0
    bond_key = []
    bond_value = []
    for key in bond_info:
        if cnt % 2 == 0:
            bond_key.append(key.getText().strip().replace(':', ''))
        else:
            bond_value.append(key.getText().strip())
        cnt += 1

    dynamic_string = '{'
    for ind in range(len(bond_key)):
        dynamic_string += "'" + str(bond_key[ind]) + "': '" + str(bond_value[ind]) + "',"
    dynamic_string += '}'

    data_record = ast.literal_eval(dynamic_string)
    if debug >= 4:  # 4
        pprint(data_record)

    return data_record


class SharePriceData:

    def __init__(self):
        self.response = requests.get(NXG_URL, headers=HEADER)
        self.ngx_page = self.response.text
        self.soup = BeautifulSoup(self.ngx_page, "html.parser")
        self.links = []
        self.symbols = []
        self.prices = []
        self.data_validated = False
        self.price_data = []

    def fetch_prices(self):
        """This fetches all prices from the Nigeria Exchange Group Site's ticker prices"""
        # print(self.soup.prettify())
        ticker_data = self.soup.find(name="div", class_="ticker")
        listings_links = ticker_data.find_all(name="a")
        prices = ticker_data.find_all(class_="ticker__list__item")

        self.links = [link.get("href") for link in listings_links]
        # link = [link for link in listings_links]
        self.symbols = [link.getText().strip() for link in listings_links]
        price_list_details = [price.getText().split(" N") for price in prices]

        price_list_details.pop(0)

        price_list_data = [data[1] for data in price_list_details]
        self.prices = [(price[:price.find(".") + 3]) for price in price_list_data]

        if len(self.symbols) == len(price_list_details) == len(price_list_data) == len(self.links) == len(self.prices):
            self.data_validated = True
            self.generate_price_json()
            if debug >= 4:  # 4
                pprint(self.price_data)

    def generate_price_json(self):
        """This populated the price_data variable with the fetched prices"""
        duplicated_url_check = ''
        duplicated_symbol = ''
        for x in range(len(self.symbols)):
            if debug >= 3:  # 3
                print('*** Checking duplicated symbol and url ***')
                print(f'{duplicated_symbol}|{duplicated_url_check}')
            if duplicated_symbol == str(self.symbols[x]) and len(duplicated_url_check) >= len(str(self.links[x])):
                pass
            elif duplicated_symbol == str(self.symbols[x]) and len(duplicated_url_check) < len(str(self.links[x])):
                del self.price_data[-1]
                self.price_data.append({'symbol': str(self.symbols[x]),
                                        'price': float(self.prices[x]),
                                        'link': str(self.links[x])
                                        })
            else:
                self.price_data.append({'symbol': str(self.symbols[x]),
                                        'price': float(self.prices[x]),
                                        'link': str(self.links[x])
                                        })

            duplicated_url_check = str(self.links[x])
            duplicated_symbol = str(self.symbols[x])
