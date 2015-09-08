import sys      # stdout.write, stdout.flush

from file_check import *

nonce_file = 'auth/nonce.sqlite'
output_file = parent_dir + 'data/output.sqlite'

check_data_files()

from print_trade_info import set_low_balance_msg, print_trade, reset_print_info
from db_access import db_connect, db_exists, output_records_exist, output_init_record, get_last_output_record, create_nonce_db
from balances import *
from analyst import *
from trader import *
from info_track import *

bal = Balance(0, 0)
timer = Timer()
info = Trade_Counter()

initial_order = True

while not db_exists(output_file):
    timer.track()
    sys.stdout.write('\rWaiting for output.sqlite to be created...%i:%i:%i' % (timer.hour, timer.min, timer.sec))
    sys.stdout.flush()
    time.sleep(1)
timer.reset()

db_connect(nonce_file, output_file)

while not output_records_exist():
    timer.track()
    sys.stdout.write('\rWaiting for first order %i:%i:%i' % (timer.hour, timer.min, timer.sec))
    sys.stdout.flush()
    time.sleep(1)
timer.reset()

balance_response = make_request('getInfo', 0, 0, 0)
bal.set_initial_balances(balance_response['return']['funds']['btc'], balance_response['return']['funds']['usd'])
bal.set_balances(balance_response['return']['funds']['btc'], balance_response['return']['funds']['usd'])

last_order_entry = output_init_record()

while True:
    output_data = get_last_output_record()
    current_row = output_data[0]
    current_price = output_data[1]
    predicted_price = output_data[2]
    order_type = output_data[3]
    err_rate = output_data[4]

    # A new output.sqlite record is present if this evaluates to true or the first record was inserted
    if current_row != last_order_entry or initial_order:
        last_order_entry = current_row
        initial_order = False

        balance_response = make_request('getInfo', 0, 0, 0)
        bal.set_balances(balance_response['return']['funds']['btc'], balance_response['return']['funds']['usd'])

        if order_type == 'buy':
            if bal.balance_check(order_type):
                usd_to_btc_qty = get_order_size(err_rate) * bal.usd_bal()
                if profit_check(order_type, usd_to_btc_qty, current_price, predicted_price):

                    if exceeds_threshold(usd_to_btc_qty / current_price):

                        prediction_buy_response = make_request(order_type, usd_to_btc_qty / current_price, current_price, 0)
                        bal.set_balances(prediction_buy_response['return']['funds']['btc'], prediction_buy_response['return']['funds']['usd'])
                        info.prediction_trade_complete()

                        #cs_args = post_trade_check(bal.btc_bal(), 'COUNTER_SELL', usd_to_btc_qty, predicted_price)

                        #counter_sell_response = make_request(cs_args[0], cs_args[1], cs_args[2], cs_args[3])
                        #info.counter_trade_complete()
                        timer.reset()
            else:
                set_low_balance_msg(str(order_type + ' order aborted - Inadequate USD balance ($' + str(bal.btc_bal()) + ')'))

        elif order_type == 'sell':
            if bal.balance_check(order_type):
                btc_to_usd_qty = get_order_size(err_rate) * bal.btc_bal()
                if profit_check(order_type, btc_to_usd_qty, current_price, predicted_price):
                    if exceeds_threshold(btc_to_usd_qty):

                        prediction_sell_response = make_request(order_type, btc_to_usd_qty, current_price, 0)
                        bal.set_balances(prediction_sell_response['return']['funds']['btc'], prediction_sell_response['return']['funds']['usd'])
                        info.prediction_trade_complete()

                        #cb_args = post_trade_check(bal.usd_bal(), 'COUNTER_BUY', btc_to_usd_qty, predicted_price)

                        #counter_buy_response = make_request(cb_args[0], cb_args[1], cb_args[2], cb_args[3])
                        #info.counter_trade_complete()
                        timer.reset()
            else:
                set_low_balance_msg(str(order_type + ' order aborted - Inadequate BTC balance (B' + str(bal.btc_bal()) + ')'))

        else:
            print('UNKNOWN ORDER TYPE')

        active_order_response = make_request('active', 0, 0, 0)
        open_btc_order_value = active_order_value(active_order_response)

        print('\r/---------------------------------------------------------------------------\\')
        print_trade()
        bal.print_bal(open_btc_order_value, current_price)
        reset_print_info()
        print('\r\---------------------------------------------------------------------------/')
    else:
        timer.track()
        sys.stdout.write('\rPrimary Trades: %i // Counter Trades: %i // Last Trade %i:%i:%i ' % (info.prediction_trades, info.counter_trades, timer.hour, timer.min, timer.sec))
        sys.stdout.flush()
        time.sleep(1)
