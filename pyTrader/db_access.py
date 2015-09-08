import sqlite3  # execute, fetchone, fetchall, commit
import os.path  # path.isFile

timeout = 15
nonce_table = 'nonce'
output_table = 'output'

def db_connect(_nonce_db_path, _output_db_path):
    global nonce_connect, nonce_cursor
    global out_connect, out_cursor

    try:
        nonce_connect = sqlite3.connect(_nonce_db_path, timeout)
        out_connect = sqlite3.connect(_output_db_path, timeout)
        nonce_cursor = nonce_connect.cursor()
        out_cursor = out_connect.cursor()
    except sqlite3.ProgrammingError as e:
        print(e)

def db_exists(_db):
    if os.path.isfile(_db):
        return True
    else:
        return False

def output_records_exist():
    out_cursor.execute('SELECT COUNT(*) FROM ' + output_table)
    data_check = out_cursor.fetchall()
    if data_check[0][0] > 0:
        return True
    else:
        return False

def output_init_record():
    out_cursor.execute('SELECT rowid, order_type FROM ' + output_table + ' ORDER BY ROWID DESC LIMIT 1')
    return out_cursor.fetchall()[0][0]

def get_last_output_record():
    out_cursor.execute('SELECT rowid, current_price, predicted_price, order_type, err_rate FROM ' + output_table + ' ORDER BY ROWID DESC LIMIT 1')
    last_record = out_cursor.fetchall()
    return last_record[0]

# Returns the nonce value anticipated by BTC-e API and increments nonce value
def get_nonce():
    nonce_cursor.execute('SELECT current_nonce FROM ' + nonce_table + ' ORDER BY current_nonce DESC LIMIT 1')
    nonce = nonce_cursor.fetchone()[0]
    nonce_cursor.execute('INSERT INTO ' + nonce_table + ' (current_nonce) VALUES(?)', [nonce + 1])
    nonce_connect.commit()
    return nonce

def adjust_nonce(_expected_nonce):
    nonce_cursor.execute('INSERT INTO ' + nonce_table + ' (current_nonce) VALUES(?)', [_expected_nonce + 1])
    nonce_connect.commit()