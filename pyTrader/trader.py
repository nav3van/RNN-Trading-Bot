from print_trade_info import set_api_resp_err, set_expected_nonce, set_api_action_msg, set_api_err
import urllib.request, urllib.parse, json, codecs, hmac, hashlib, http.client
from db_access import get_nonce, adjust_nonce

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

with open('auth/api-credentials.json', 'r') as credential_file:
    _credentials_ = json.load(credential_file)
    credential_file.close()

api_key = _credentials_['api_key']
api_secret = _credentials_['api_secret']
api_secret = api_secret.encode('ascii')

def api_error_check(_api_response, _action, _btc_qty, _price, _order_num):
    if _api_response['success'] != 1:
        if 'error' in _api_response:
            set_api_resp_err(str(_api_response))###
            invalid_nonce = 'invalid nonce parameter'
            if invalid_nonce in _api_response['error']:
                expected_nonce = _api_response['error'].split('you should send:', 1)[1]
                set_expected_nonce(str(expected_nonce))###
                adjust_nonce(expected_nonce)
                make_request(_action, _btc_qty, _price, _order_num)

# Returns the current parameters required to make a valid request based on _action given as argument
def get_params(_nonce, _action, _btc, _price, _order_num):

    _btc = float("{0:.3f}".format(_btc))
    _price = float("{0:.3f}".format(_price))

    if _action == 'buy':
        p = { 'method':'Trade', 'pair':'btc_usd','type':'buy','rate':_price,'amount':_btc, 'nonce':_nonce }
    elif _action == 'sell':
        p = { 'method':'Trade', 'pair':'btc_usd','type':'sell','rate':_price,'amount':_btc,'nonce':_nonce }
    elif _action == 'active':
        p = { 'method':'ActiveOrders', 'nonce':_nonce }
    elif _action == 'info':
        p = { 'method':'OrderInfo', 'order_id':_order_num,'nonce':_nonce }
    elif _action == 'cancel':
        p = { "method":"CancelOrder", 'order_id':_order_num, 'nonce':_nonce }
    else:
        p = { 'method':'getInfo','nonce':_nonce }
    param_p = urllib.parse.urlencode(p)
    return param_p.encode('ascii')


# Returns JSON response from BTC-e API dependant on _action given as argument
def make_request(_action, _btc_qty, _price, _order_num):
    attempts = 0
    conn = http.client.HTTPSConnection('btc-e.com')
    params = get_params(get_nonce(), _action, _btc_qty, _price, _order_num)
    H = hmac.new(api_secret, digestmod=hashlib.sha512)
    H.update(params)
    sign = H.hexdigest()
    headers = {'Content-type':'application/x-www-form-urlencoded','Key':api_key,'Sign':sign}

    # Attempt HTTP request up to 5 times if valid response not received on prior requests
    while attempts < 5:
        try:
            conn.request('POST','/tapi', params, headers)
            response = conn.getresponse()
            reader = codecs.getreader('utf-8')
            api_json_response = json.load(reader(response))

            api_error_check(api_json_response, _action, _btc_qty, _price, _order_num)

            if _action != 'getInfo':
                set_api_action_msg(str(_action + ' request complete'))

            return api_json_response

        except urllib.request.HTTPError as err:
            attempts += 1
            set_api_err(str(err.code), err.read())
