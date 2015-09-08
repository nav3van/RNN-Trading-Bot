#ifndef EXCHANGE_H
#define EXCHANGE_H

#include <stdio.h>
#include <iostream>
#include <string>
#include "sqlite3.h"

enum Trade { BUY, SELL, WAIT };

class Exchange
{
public:
  Exchange();
  void StoreOutput(double current_price, double predicted_price, enum Trade order_type, double error_rate);
  void Set_last_price_(double price);
  Trade GetTrade(double current_price, double predicted_price);
  void log(enum Trade order_type, double predicted_price);
private:
  double usd_balance_;
  double btc_balance_;
  double purchase_price;
  double last_price_;

  int rc_;
  sqlite3 *output_db_;
  const char* output_data_file_ = "/home/evan/hdd1/programming/projects/ann_trading_bot/data/output.sqlite";
  //const char* output_data_file_ = "output.sqlite";
  std::string output_data_table_ = "output";;
  char *z_err_msg_ = 0;
  const int output_db_timeout = 5000;
};

#endif
