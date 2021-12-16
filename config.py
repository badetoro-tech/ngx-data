from datetime import datetime

ngx_url = "https://ngxgroup.com/"

header = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/96.0.4664.45 Safari/537.36",
    "Accept-Language": "en-US;en;"
}

demo_user = 'demo'
page_upd = False
debug = 0
wait_time = 5

today = datetime.today().date()
if today.isoweekday() == 7 and today.day <= 7:
    page_upd = True
