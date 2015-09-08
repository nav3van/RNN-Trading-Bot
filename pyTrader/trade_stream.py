import os, sys, time, datetime
import urllib.request, urllib.parse, json, codecs, socket
from file_check import parent_dir


# Dynamically imports the class required for the extension returned by get_output_type
# Returns the name of the class and the imported module containing that class
def import_class_module():
    module = 'sqlite_output'
    temp_class_name = 'sqlite_obj'
    temp_imported_class = __import__(module, fromlist=temp_class_name)
    return temp_class_name, temp_imported_class


# Continue asking user for input if an entry that does not correlate to an index of _extension_list is entered
# Return user entry once a valid input has been made
def get_user_input(_extension_list):
    while True:
        try:
            usr_input = int(input())
        except ValueError:
            print('***Invalid Input***\nEnter a number from 0 to ' + str(len(_extension_list) - 1) + ' inclusive')
            continue
        else:
            if usr_input < 0 or usr_input >= len(_extension_list):
                print('***Invalid Input***\nEnter a number from 0 to ' + str(len(_extension_list) - 1) + ' inclusive')
            else:
                return usr_input

# Returns true if api response contains valid data and false otherwise
def valid_response(_json_resp):
    err_originator_desc = 'json response validation'
    try:
        if 'btc_usd' not in _json_resp:
            return False
    except ValueError as e:
        store_log([err_originator_desc,e])
    return True

# Returns BTC-e API response with current exchange rates
def http_request():
    max_requests = 10

    # Specifies how long a socket should wait for a response before timing out
    socket.setdefaulttimeout(socket_timeout)

    while max_requests > 0:
        try:
            api_request = urllib.request.Request(url, headers=headers)
            api_response = urllib.request.urlopen(api_request)
            json_response = json.load(reader(api_response))

            if valid_response(json_response):
                return json_response
            else:
                store_log(['***Bad response***', str(json_response)])
        except urllib.request.HTTPError as e:
            print('e1')
            store_log(['receiving api response', e])
        except Exception as e:
            print('e2')
            store_log(['api request', e])

        max_requests -= 1
        time.sleep(2)

    print('***API request threshold met with no valid responses received***')


def get_trade_data():
    while True:
        json_obj = http_request()

        g_output_object.open_output_file()
        timestamp = datetime.datetime.fromtimestamp(int(json_obj['btc_usd']['updated'])).strftime('%Y%m%d%H%M%S')
        g_output_object.store_output(timestamp, json_obj['btc_usd']['sell'], json_obj['btc_usd']['buy'])

        sys.stdout.write("\rTrade record count = %i" % g_output_object.record_count())
        sys.stdout.flush()
        time.sleep(2)


def store_log(_argv):
    with open(parent_dir + 'data/error.log', 'a+') as log_file:
        log_file.write('\n/-------------------\\\n')
        for argc in _argv:
            if argc == _argv[0]:
                log_file.write('Error occurred during ' + argc + ' at ' + str(datetime.datetime.now()))
            else:
                log_file.write(str(argc))
        log_file.write('\n\\-------------------/\n')
    log_file.close()


current_dir_oath = os.path.realpath(os.path.dirname(''))
out_dir_path = parent_dir + 'data/'
out_file_name = 'input.sqlite'

socket_timeout = 15
url = 'https://btc-e.com/api/3/ticker/btc_usd'
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.17 (KHTML, like Gecko) Chrome/24.0.1312.27 Safari/537.17'}
reader = codecs.getreader('utf-8')


def main():
    class_name, imported_class = import_class_module()
    mod_attr = getattr(imported_class, class_name)
    output_path = out_dir_path + out_file_name

    global g_output_object
    g_output_object = mod_attr(output_path)

    # http_request() is wrapped in an infinite loop. If an exception is encountered during http_request(),
    # the local infinite loop within that function will break. However, the infinite loop below will prevent
    # execution from stopping.
    while True:
        get_trade_data()
        store_log(['http_request() infinite loop', ['Pausing for 2 seconds before re-initiating request sequence']])
        time.sleep(2)


if __name__ == '__main__':
    main()
