from price_data import SharePriceData, extract_equity_info, extract_bond_info
from models import metadata, daily_price, equity_info, instruments, bond_info, exc_fund_info
from database import engine
from sqlalchemy import select, and_, update, insert
from sqlalchemy.exc import IntegrityError
from pprint import pprint
import time
from datetime import datetime
from config import wait_time, demo_user, page_upd, debug

# db = SessionLocal()
metadata.create_all(engine)
connection = engine.connect()

# get all share prices
share_price_data = SharePriceData()
share_price_data.fetch_prices()


def populate_data(current_date):
    # Populate the instruments table with data
    if page_upd:
        print(f'*** To update all pages details on first Sunday of the month ***')

    populate_instruments_data()
    populate_daily_price_data(current_date)

    populate_equity_info_data()
    populate_bond_info_data()


def populate_instruments_data():
    if debug >= 1:  # 1
        print(f'*** Executing populate_instruments_data ... ***')
    stmt = select([instruments.c.symbol, instruments.c.name, instruments.c.ins_type, instruments.c.ins_details_url])
    query_result = connection.execute(stmt).fetchall()

    if debug >= 4:  # 4
        print(str(stmt))
    if debug >= 4:  # 4
        print(query_result)

    # if price result is empty, insert records into the two tables
    symbol_data = []
    for x in share_price_data.price_data:

        # check if price_data.symbol exists in query_result
        if list(filter(lambda query: query['symbol'] == x['symbol'], query_result)):
            # if price_data.symbol exists in query_result
            # sub_q = next((item for item in query_result if item["symbol"] == x['symbol']), False)
            # print('********')
            # print(sub_q)

            if debug >= 2:  # 2
                print(f"{x['symbol']} exists already ....")

            if page_upd:
                if debug >= 2:  # 2
                    print(f"Updating instruments table for {x['symbol']} ....")
                try:
                    u = update(instruments).where(instruments.c.symbol == x['symbol'])
                    u = u.values(ins_details_url=(x['link']), modified_by=demo_user)
                    if debug >= 4:  # 4
                        print(str(u))
                    connection.execute(u)
                except AttributeError as error:
                    print(error)

        else:
            if debug >= 2:  # 2
                print(f"{x['symbol']} does not exist. Generating inserting statement ...")
            generate_int_data(symbol_data, x['symbol'], x['link'], demo_user)

    # insert symbols with blank data into Equity Info
    if debug >= 3:  # 3
        print('Printing query to insert into instruments table: symbol_data ...')
        pprint(symbol_data)
    try:
        ins = insert(instruments)
        if len(symbol_data) > 0:
            connection.execute(ins, symbol_data)
    except IntegrityError as error:
        print(error)


def populate_daily_price_data(current_date):
    if debug >= 1:  # 1
        print(f'*** Executing populate_daily_price_data ... ***')
    stmt = select([daily_price.c.symbol, daily_price.c.value_date, daily_price.c.amount])
    stmt = stmt.where(daily_price.c.value_date == current_date)
    query_result = connection.execute(stmt).fetchall()

    if debug >= 4:  # 4
        print(str(stmt))
    if debug >= 4:  # 4
        print(query_result)

    daily_price_data = []
    for x in share_price_data.price_data:
        # check if price_data.symbol exists in query_result
        if list(filter(lambda query: query['symbol'] == x['symbol'], query_result)):
            if debug >= 2:  # 2
                print(f"{x['symbol']} exists already for the day, updating ....")
            u = update(daily_price).where(
                and_(daily_price.c.symbol == x['symbol'],
                     daily_price.c.value_date == current_date)
            )
            u = u.values(amount=(x['price']), modified_by=demo_user)
            if debug >= 4:  # 4
                print(str(u))
            connection.execute(u)
        else:
            if debug >= 2:  # 2
                print(f"{x['symbol']} does not exist for the day.Inserting ....")
            gen_daily_price_data(daily_price_data, current_date, x['symbol'], x['price'], demo_user)

    try:
        # insert price data for the day into daily_price table
        ins = insert(daily_price)
        if len(daily_price_data) > 0:
            connection.execute(ins, daily_price_data)
    except IntegrityError as error:
        print(error)


def populate_equity_info_data():
    if debug >= 1:  # 1
        print(f'*** Executing populate_equity_info_data ... ***')
    stmt = select([instruments.c.symbol, instruments.c.name, instruments.c.ins_details_url])
    stmt = stmt.where(instruments.c.ins_type == 1)
    query_result = connection.execute(stmt).fetchall()

    for record in query_result:
        to_wait = False
        page_url = record['ins_details_url']
        if record['symbol'] == record['name']:
            to_wait = True
            try:
                extracted_data = extract_equity_info(page_url)
            except AttributeError as error:
                print(error)
                u = update(instruments).where(instruments.c.symbol == record['symbol'])
                u = u.values(name='', modified_by=demo_user)
                if debug >= 4:  # 4
                    print(str(u))
                connection.execute(u)
            else:
                if debug >= 2:  # 2
                    print(f"{record['symbol']} has never been updated, now updating ....")
                try:
                    u = update(instruments).where(instruments.c.symbol == record['symbol'])
                    u = u.values(name=(str(extracted_data['CompanyName'])), modified_by=demo_user)
                    if debug >= 4:  # 4
                        print(str(u))
                        pprint(extracted_data)
                    connection.execute(u)

                except AttributeError as error:
                    print(error)

                try:
                    # insert equity details into equity_info table
                    ins = insert(equity_info)
                    equity_data = {
                        'symbol': record['symbol'],
                        'trading_name': extracted_data['CompanyName'],
                        'ticker': extracted_data['Symbol'],
                        'sector': extracted_data['Sector'],
                        'sub_sector': extracted_data['SubSector'].replace('\"', ''),
                        'market_classification': extracted_data['MarketClassification'],
                        'nature_of_business': extracted_data['Nature of Business'],
                        'market_cap_million': float(extracted_data['MarketCap'].replace(',', '')),
                        'shares_outstanding_million': float(extracted_data['SharesOutstanding'].replace(',', '')),
                        'date_listed': datetime.strptime(extracted_data['Date Listed'], '%b-%d-%Y'),
                        'created_by': demo_user
                    }
                    if len(equity_data) > 0:
                        connection.execute(ins, equity_data)
                except IntegrityError as error:
                    print(error)

        elif record['symbol'] != record['name'] and page_upd:
            to_wait = True
            try:
                extracted_data = extract_equity_info(page_url)
            except AttributeError as error:
                print(error)
            else:
                if equity_info.c.symbol == record['symbol'] and \
                        (equity_info.c.market_cap_million != float(extracted_data['MarketCap'].replace(',', ''))
                         or equity_info.c.date_listed != datetime.strptime(extracted_data['Date Listed'], '%b-%d-%Y')
                         or equity_info.c.shares_outstanding_million !=
                         float(extracted_data['SharesOutstanding'].replace(',', ''))
                         or equity_info.c.trading_name != str(extracted_data['CompanyName'])):
                    if debug >= 2:  # 2
                        print(f"{record['symbol']} now updating ....")
                    try:
                        u = update(instruments).where(instruments.c.symbol == record['symbol'])
                        u = u.values(name=(str(extracted_data['CompanyName'])), modified_by=demo_user)
                        if debug >= 4:  # 4
                            print(str(u))
                            pprint(extracted_data)
                        connection.execute(u)
                    except AttributeError as error:
                        print(error)
                    try:
                        u = update(equity_info).where(equity_info.c.symbol == record['symbol'])
                        u = u.values(trading_name=(str(extracted_data['CompanyName'])),
                                     ticker=(extracted_data['Symbol']),
                                     sector=(extracted_data['Sector']),
                                     sub_sector=extracted_data['SubSector'].replace('\"', ''),
                                     market_classification=extracted_data['MarketClassification'],
                                     nature_of_business=extracted_data['Nature of Business'],
                                     market_cap_million=float(extracted_data['MarketCap'].replace(',', '')),
                                     shares_outstanding_million=float(extracted_data['SharesOutstanding'].replace
                                                                      (',', '')),
                                     date_listed=datetime.strptime(extracted_data['Date Listed'], '%b-%d-%Y'),
                                     modified_by=demo_user)
                        if debug >= 4:  # 4
                            print(str(u))
                            pprint(extracted_data)
                        connection.execute(u)
                    except AttributeError as error:
                        print(error)

        if to_wait:
            time.sleep(wait_time)


def populate_bond_info_data():
    if debug >= 1:  # 1
        print(f'*** Executing populate_bond_info_data ... ***')
    stmt = select([instruments.c.symbol, instruments.c.name, instruments.c.ins_details_url])
    stmt = stmt.where(instruments.c.ins_type == 2)
    query_result = connection.execute(stmt).fetchall()

    for record in query_result:
        to_wait = False
        page_url = record['ins_details_url']
        if record['symbol'] == record['name']:
            to_wait = True
            try:
                extracted_data = extract_bond_info(page_url)
            except AttributeError as error:
                print(error)
                u = update(instruments).where(instruments.c.symbol == record['symbol'])
                u = u.values(name='', modified_by=demo_user)
                if debug >= 4:  # 4
                    print(str(u))
                connection.execute(u)
            else:
                if debug >= 2:  # 2
                    print(f"{record['symbol']} has never been updated, now updating ....")
                try:
                    u = update(instruments).where(instruments.c.symbol == record['symbol'])
                    u = u.values(name=(str(extracted_data['Issuer'] + ' | ' + extracted_data['Bond Type'])),
                                 modified_by=demo_user)
                    if debug >= 4:  # 4
                        print(str(u))
                        pprint(extracted_data)
                    connection.execute(u)
                except AttributeError as error:
                    print(error)

                try:
                    # insert bond details into bond_info table
                    ins = insert(bond_info)
                    bond_data = {
                        'symbol': record['symbol'],
                        'issuer': extracted_data['Issuer'],
                        'description': extracted_data['Description'],
                        'face_value': float(extracted_data['Face Value (₦)'].replace(',', '')),
                        'issue_no': extracted_data['ISIN'],
                        'issue_date': datetime.strptime(extracted_data['Issue Date'].replace('--', 'Jan-01-1970')
                                                        , '%b-%d-%Y'),
                        'maturity_date': datetime.strptime(extracted_data['Maturity Date'], '%b-%d-%Y'),
                        'coupon': float(extracted_data['Coupon'].replace('--', '0')),
                        'issue_price': float(extracted_data['Issue Price (₦)'].replace('--', '0')),
                        'bond_type': extracted_data['Bond Type'],
                        'created_by': demo_user
                    }
                    if len(bond_data) > 0:
                        connection.execute(ins, bond_data)
                except IntegrityError as error:
                    print(error)

        elif record['symbol'] != record['name'] and page_upd:
            to_wait = True
            try:
                extracted_data = extract_bond_info(page_url)
            except AttributeError as error:
                print(error)
            else:
                if bond_info.c.symbol == record['symbol'] and bond_info.c.issue_no != extracted_data['ISIN']:
                    if debug >= 2:  # 2
                        print(f"{record['symbol']} now updating ....")

                    try:
                        u = update(instruments).where(instruments.c.symbol == record['symbol'])
                        u = u.values(name=(str(extracted_data['Issuer'] + ' | ' + extracted_data['Bond Type'])),
                                     modified_by=demo_user)
                        if debug >= 4:  # 4
                            print(str(u))
                            pprint(extracted_data)
                        connection.execute(u)
                    except AttributeError as error:
                        print(error)
                    try:
                        u = update(bond_info).where(bond_info.c.symbol == record['symbol'])
                        u = u.values(issuer=(str(extracted_data['Issuer'])),
                                     description=extracted_data['Description'],
                                     face_value=float(extracted_data['Face Value (₦)'].replace(',', '')),
                                     issue_no=extracted_data['ISIN'],
                                     issue_date=datetime.strptime(extracted_data['Issue Date'].replace
                                                                  ('--', 'Jan-01-1970'), '%b-%d-%Y'),
                                     maturity_date=datetime.strptime(extracted_data['Maturity Date'], '%b-%d-%Y'),
                                     coupon=float(extracted_data['Coupon'].replace('--', '0')),
                                     issue_price=float(extracted_data['Issue Price (₦)'].replace('--', '0')),
                                     bond_type=extracted_data['Bond Type'],
                                     created_by=demo_user)
                        if debug >= 4:  # 4
                            print(str(u))
                            pprint(extracted_data)
                        connection.execute(u)
                    except AttributeError as error:
                        print(error)

        if to_wait:
            time.sleep(wait_time)


def generate_int_data(symbol_data, symbol, link, created_by):
    if link.find('bonddirectory') >= 0:
        # is a bond instrument
        ins_type = 2
    elif link.find('etpdirectory') >= 0:
        # is an exchange traded instrument
        ins_type = 3
    elif link.find('companydirectory') >= 0:
        # is an equity instrument
        ins_type = 1
    else:
        ins_type = 0

    symbol_data.append(
        {
            'symbol': symbol,
            'name': symbol,
            'ins_type': ins_type,
            'ins_details_url': link,
            'created_by': created_by
        }
    )


def gen_daily_price_data(daily_price_data, current_date, symbol, price, created_by):
    daily_price_data.append(
        {
            'symbol': symbol,
            'value_date': current_date,
            'amount': price,
            'created_by': created_by
        }
    )
# class StartupData:
#
#     def __init__(self):
#         pass
