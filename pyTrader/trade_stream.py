import urllib.request
import urllib.parse
import json
import socket
import codecs
import sqlite3
import time
import sys

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
reader = codecs.getreader("utf-8")

url = 'https://btc-e.com/api/3/ticker/btc_usd'

input_file = '/home/evan/hdd1/programming/projects/ann_trading_bot/data/input.sqlite'
print(input_file)
table_name = "price_data"

db_timeout = 15
socket_timeout = 15

# Specifies how long a socket should wait for a response before timing out
socket.setdefaulttimeout(socket_timeout)

connect = sqlite3.connect(input_file, db_timeout)
cursor = connect.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS " + table_name + " (vol DOUBLE, buy DOUBLE, sell DOUBLE, vol_cur DOUBLE, last DOUBLE)")


def create_comparison_json(buy, sell, last):
    data = {'buy':buy, 'sell':sell, 'last':last}
    return json.dumps(data)

# Allows first response to be inserted as there is no prior response to compare against
initial_pass_flag = True

# Contain JSON of prior API response to compare with current response to check for uniqueness
prior = {}

# Attempt HTTP request
# If http request fails, attempt it up to 5 times in total, up to 4 additional attempts after initial request
# If request fails after 5 attempts, execution does not continue
while True:
    attempts = 0
    while attempts < 5:
        try:
            api_request = urllib.request.Request(url, headers=headers)
            api_response = urllib.request.urlopen(api_request)
            json_obj = json.load(reader(api_response))
            break
        except urllib.request.HTTPError as err:
            attempts += 1
            print(err.code)
            print(err.read())

    current = create_comparison_json(json_obj['btc_usd']['buy'], json_obj['btc_usd']['sell'], json_obj['btc_usd']['last'])

    try:
        if current != prior or initial_pass_flag:
            cursor.execute("INSERT INTO " + table_name + " (vol, buy, sell, vol_cur, last) values(?,?,?,?,?)",
                   (json_obj['btc_usd']['vol'], json_obj['btc_usd']['buy'], json_obj['btc_usd']['sell'],
                    json_obj['btc_usd']['vol_cur'], json_obj['btc_usd']['last']))
            connect.commit()

            prior = create_comparison_json(json_obj['btc_usd']['buy'], json_obj['btc_usd']['sell'], json_obj['btc_usd']['last'])
            initial_pass_flag = False

        cursor.execute("SELECT COUNT(*) FROM " + table_name)
        record_count = cursor.fetchone()[0]

        sys.stdout.write("\rTrade record count = %i" % record_count)
        sys.stdout.flush()
    except sqlite3.ProgrammingError as e:
        print(e)

    # BTC-e API updates every 2 seconds. Submitting requests more frequently results in duplicate responses
    time.sleep(2)
