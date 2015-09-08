from print_trade_info import set_expected_profit, set_profit_notice, set_profit_err, set_counter_msg, set_threshold_err

# Exchange fee (0.2%) deducted from every trade
fee = 0.002

# minimum profit margin (0.3%) for a trade to be executed
min_margin = 0.001

# minimum value of a trade allowed on BTC-e
trade_min = 0.01

# Returns true if (taking exchange trading fees into consideration) the quantity of BTC/USD bot could BUY/SELL
#   presently is > the amount it could BUY/SELL at the predicted price, and the difference between BUYING/SELLING now
#   vs waiting to BUY/SELL is > the set profit margin threshold
def profit_check(_order_type, _order_size, _current_price, _predicted_price):
    # _order_size is a USD value for sell orders
    if _order_type == 'buy':
        BTC_buy_at_current = _order_size / _current_price
        BTC_sell_at_predicted = _order_size / _predicted_price

        if BTC_buy_at_current > BTC_sell_at_predicted:
            set_expected_profit(str(_order_type + ' Expected BTC gain: B' + str(BTC_sell_at_predicted - BTC_buy_at_current)))
            trade_profit = 1 - ((BTC_sell_at_predicted - BTC_buy_at_current) / BTC_buy_at_current)
            if trade_profit > min_margin:
                return True
            else:
                set_profit_notice(str('BUYING will yield less than ' + str(min_margin) + '% profit ' + str(trade_profit) + '%'))
                return False
        else:
            set_profit_notice(str('BUYING at current (B' + str("{0:.8f}".format(BTC_buy_at_current)) + ') and selling at predicted (B' + str("{0:.8f}".format(BTC_sell_at_predicted)) + ') is unprofitable'))
            return False

    # _order_size is a BTC value for sell orders
    elif _order_type == 'sell':
        BTC_sell_at_current = (_order_size * _current_price) / _current_price
        BTC_buy_at_predicted = (_order_size * _predicted_price) / _predicted_price

        if BTC_buy_at_predicted > BTC_sell_at_current:
            set_expected_profit(str('Expected BTC gain: B' + str(BTC_buy_at_predicted - BTC_sell_at_current)))
            trade_profit = 1 - ((BTC_buy_at_predicted - BTC_sell_at_current) / BTC_sell_at_current)
            if trade_profit > min_margin:
                return True
            else:
                set_profit_notice(str('SELLING will yield less than ' + str(min_margin) + '% profit ' + str(trade_profit) + '%'))
                return False
        else:
            set_profit_notice(str('SELLING at current (B' + str("{0:.8f}".format(BTC_sell_at_current)) + ') and BUYING at predicted (B' + str("{0:.8f}".format(BTC_buy_at_predicted)) + ') is unprofitable'))
            return False
    else:
        set_profit_err('PROFIT CHECK ERROR')
        return False

def post_trade_check(_bal_qty, _action, _order_size,_predicted_price):
    if _action == 'COUNTER_BUY':
        # _order_size is a BTC value for COUNTER_BUY orders
        if _order_size >= trade_min:
            set_counter_msg(str('Preparing counter buy for B' + str(_order_size)))
            return ['buy', _order_size, _predicted_price, 0]
        elif (_bal_qty / _predicted_price) - (fee * (_bal_qty / _predicted_price)) >= trade_min:
            set_counter_msg(str('Original counter buy < B' + str(trade_min) + ' (B' + str(_order_size) + '), increased counter buy size to B' + str(trade_min)))
            return ['buy', trade_min, _predicted_price, 0]
        else:
            set_counter_msg(str('BTC value of USD balance < B' + str(trade_min) + ' ($' + str(_bal_qty) + '), unable to place counter buy'))
            return ['getInfo', 0, 0, 0]

    elif _action == 'COUNTER_SELL':
        # _order_size is a USD value for COUNTER_SELL orders
        if _order_size / _predicted_price >= trade_min:
            set_counter_msg(str('Preparing counter sell for B' + str(_order_size / _predicted_price)))
            return ['sell', _order_size / _predicted_price, _predicted_price, 0]
        elif _bal_qty - (fee * _bal_qty) >= trade_min:
            set_counter_msg(str('Original counter sell < B' + str(trade_min) + ' (B' + str(_order_size / _predicted_price) + '), increased counter sell size to B' + str(trade_min)))
            return ['sell', trade_min, _predicted_price, 0]
        else:
            set_counter_msg(str('BTC balance < B' + str(trade_min) + ', unable to place counter sell'))
            return ['getInfo', 0, 0, 0]

# Returns the percentage of current BTC/USD balance to use as the size of the current order
def get_order_size(_error_rate):
    if _error_rate < 0.0005:
        return 0.2
    elif _error_rate < 0.005:
        return 0.15
    elif _error_rate < 0.05:
        return 0.1
    else:
        return 0.05

def exceeds_threshold(_btc_trade_value):
    if _btc_trade_value - (_btc_trade_value * fee) >= trade_min:
        return True
    else:
        set_threshold_err(str('**Trade value = ' + str(_btc_trade_value) + ' - BTC value of order must be >= ' + str(trade_min) + ' BTC'))
        return False

def active_order_value(_active_order_response):
    open_value = 0
    open_orders = _active_order_response['return'].keys()
    for order in open_orders:
        open_value += _active_order_response['return'][str(order)]['amount']
    return open_value