# from price_data import SharePriceData
from setup_db import check_setup_data
import query
from datetime import datetime, timedelta
from models import metadata
from database import engine
from config import debug, demo_user, page_upd

# initialise local variables
today = datetime.today().date()
demo_user = demo_user
page_upd = page_upd
debug = debug

start_time = datetime.now()
if debug >= 0:
    print(f'*** Starting program at {start_time.strftime("%d-%b-%Y %I:%M:%S.%f %p")} ***')

# db = SessionLocal()
metadata.create_all(engine)
connection = engine.connect()

# check if today is weekend and set to prev working day
current_date = today
if today.isoweekday() > 5:
    current_date = today - timedelta(days=(today.isoweekday() - 5))

if debug >= 0:
    print(f'*** Running as current date: {str(current_date)} ***')

# initialize setup data
check_setup_data(debug)

# # get all share prices
# share_price_data = SharePriceData()
# share_price_data.fetch_prices()

# Populating tables with extracted data
x = query.populate_data(current_date)

finish_time = datetime.now()
if debug >= 0:
    print(f'*** Finished program at {finish_time.strftime("%d-%b-%Y %I:%M:%S.%f %p")} ***')
    print(f'*** Time to complete - {finish_time - start_time} ***')
