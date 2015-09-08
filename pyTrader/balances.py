class Balance(object):
    def __init__(self, _btc, _usd):
        self.initial_btc = _btc
        self.initial_usd = _usd
        self.btc = _btc
        self.usd = _usd
        self.profit = 0

    def set_initial_balances(self, _btc, _usd):
        self.initial_btc = _btc
        self.initial_usd = _usd

    def set_balances(self, _btc, _usd):
        self.btc = _btc
        self.usd = _usd

    def btc_bal(self):
        return self.btc

    def usd_bal(self):
        return self.usd

    def balance_check(self, _order_type):
        if _order_type == 'buy':
            if self.usd == 0:
                return False
            else:
                return True
        elif _order_type == 'sell':
            if self.btc == 0:
                return False
            else:
                return True

    def print_bal(self, _open_btc_value, _current_price):
        print('btc.....B' + str(self.btc))
        print('usd.....$' + str(self.usd))
        print('open....B' + str("{0:.8f}".format(_open_btc_value)))
        print('TOTAL...B' + str("{0:.8f}".format(self.btc + (self.usd / _current_price) + _open_btc_value)))

        if self.btc - self.initial_btc == 0 or self.initial_btc == 0:
            self.profit = 0
        else:
            self.profit = (self.btc - self.initial_btc + _open_btc_value) / self.initial_btc

        print('profit...' + str("{0:.8f}".format(self.profit) + '%'))
