def set_low_balance_msg(_msg):
    m[0] += _msg

def set_expected_profit(_msg):
    msgs[1] += _msg

def set_profit_notice(_msg):
    msgs[2] += _msg

def set_profit_err(_msg):
    msgs[3] += _msg

def set_counter_msg(_msg):
    msgs[4] += _msg

def set_threshold_err(_msg):
    msgs[5] += _msg

def set_api_resp_err(_msg):
    msgs[6] += _msg

def set_expected_nonce(_msg):
    msgs[7] += _msg

def set_api_action_msg(_msg):
    msgs[8] += _msg

def set_api_err(_code, _msg):
    msgs[9] += str('Code: ' + _code + ', ' + _msg)

m = ['**','Expected Profit: ','>>> ','Profit Error: ','Counter Message: ','Threshold Error: ','API Response Error: ','Expected Nonce Error: ','Action: ','API Error: ']

msgs = ['**','Expected Profit: ','>>> ','Profit Error: ','Counter Message: ','Threshold Error: ','API Response Error: ','Expected Nonce Error: ','Action: ','API Error: ']

def reset_print_info():
    i = 0
    for msg in msgs:
        msgs[i] = m[i]
        i += 1

def print_trade():
    i = 0
    for msg in msgs:
        if len(msgs[i]) > len(m[i]):
            print('\r' + msgs[i])
        i += 1
