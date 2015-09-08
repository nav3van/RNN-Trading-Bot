class Timer(object):
    def __init__(self):
        self.sec = 0
        self.min = 0
        self.hour = 0
    def track(self):
        if self.sec == 59:
            self.sec = 0
            self.min += 1
            if self.min == 60:
                self.min = 0
                self.hour += 1
        else:
            self.sec += 1
    def get_time(self):
        return [self.min, self.sec]
    def reset(self):
        self.sec = 0
        self.min = 0
        self.hour = 0

class Trade_Counter(object):
    def __init__(self):
        self.prediction_trades = 0
        self.counter_trades = 0
    def prediction_trade_complete(self):
        self.prediction_trades += 1
    def counter_trade_complete(self):
        self.counter_trades += 1
    def get_trade_info(self):
        return [self.prediction_trades, self.counter_trades]
