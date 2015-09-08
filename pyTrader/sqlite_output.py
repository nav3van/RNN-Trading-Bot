import sqlite3
from trade_stream import store_log

class sqlite_obj(object):
    def __init__(self, _output_path):
        err_originator_desc = 'initializing sqlite_obj'
        self.db_path = _output_path
        self.table_name = 'trade_data'
        self.db_timeout = 15

        # establish initial connection to db
        try:
            self.db_connect = sqlite3.connect(self.db_path, self.db_timeout)
            self.cursor = self.db_connect.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table_name + " (timestamp INTEGER, buy DOUBLE, sell DOUBLE)")
        except sqlite3.ProgrammingError as e:
            store_log([err_originator_desc, e])
        except Exception as e:
            store_log([err_originator_desc, e])

    # Store connection to output db for current object after establishing connection
    def open_output_file(self):
        err_originator_desc = 'opening sqlite db'
        try:
            self.db_connect = sqlite3.connect(self.db_path, self.db_timeout)
            self.cursor = self.db_connect.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS " + self.table_name + " (timestamp INTEGER, buy DOUBLE, sell DOUBLE)")
        except sqlite3.ProgrammingError as e:
            store_log([err_originator_desc, e])
        except Exception as e:
            store_log([err_originator_desc, e])

    # Insert new record to output db and close output file
    def store_output(self, _timestamp, _bid, _ask):
        err_originator_desc = 'sqlite insert operation'
        try:
            self.cursor.execute("INSERT INTO " + self.table_name + " (timestamp, buy, sell) values(?,?,?)", (_timestamp, _bid, _ask))
            self.db_connect.commit()
        except sqlite3.ProgrammingError as e:
            self.db_connect.close()
            store_log([err_originator_desc, e])
        except IOError as e:
            self.db_connect.close()
            store_log([err_originator_desc, e])
        except Exception as e:
            store_log([err_originator_desc, e])

    # Count the number of records that exist in output db, close output db, return the total record count
    def record_count(self):
        err_originator_desc = 'sqlite record count operation'
        try:
            self.cursor.execute("SELECT COUNT(*) FROM " + self.table_name)
            return self.cursor.fetchone()[0]
        except sqlite3.ProgrammingError as e:
            self.db_connect.close()
            store_log([err_originator_desc, e])
        except Exception as e:
            store_log([err_originator_desc, e])



