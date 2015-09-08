#include "exchange.h"

// Post Conditions
// - output.sqlite is created if it does not exist and opened
// - output table is created in output.sqlite with columns current_price, predicted_price, order_type, err_rate
Exchange::Exchange()
{
  rc_ = sqlite3_open(output_data_file_, &output_db_);

  if (rc_ != SQLITE_OK)
  {
    fprintf(stderr, "SQL error: %s\n", z_err_msg_);
    sqlite3_free(z_err_msg_);
  }

  std::string sql_string = "CREATE TABLE IF NOT EXISTS " + output_data_table_ + " (current_price DOUBLE, predicted_price DOUBLE, order_type TEXT, err_rate DOUBLE);";
  const char* sql = sql_string.c_str();

  sqlite3_busy_timeout(output_db_, output_db_timeout);
  rc_ = sqlite3_exec(output_db_, sql, 0, 0, &z_err_msg_);

  if (rc_ != SQLITE_OK)
  {
    fprintf(stderr, "SQL error: %s\n", z_err_msg_);
    sqlite3_free(z_err_msg_);
  }
}

void Exchange::StoreOutput(double current_price, double predicted_price, enum Trade order_type, double error_rate)
{
  if (order_type != WAIT)
  {
  	std::string order;

  	if (order_type == BUY)
  		order = "buy";
  	else
  		order = "sell";

    std::string sql_string = "INSERT INTO " + output_data_table_ + " (current_price, predicted_price, order_type, err_rate) values('" +
      std::to_string(current_price) + "', '" + std::to_string(predicted_price) + "','" + order + "','" + std::to_string(error_rate) + "');";

    const char* sql = sql_string.c_str();
    sqlite3_busy_timeout(output_db_, output_db_timeout);
    rc_ = sqlite3_exec(output_db_, sql, 0, 0, &z_err_msg_);

    if (rc_ != SQLITE_OK)
    {
      fprintf(stderr, "SQL error: %s\n", z_err_msg_);
      sqlite3_free(z_err_msg_);
    }
  }
}

void Exchange::Set_last_price_(double price)
{
  last_price_ = price;
}

Trade Exchange::GetTrade(double current_price, double predicted_price)
{
  if (predicted_price > current_price)
  {
    log(BUY, predicted_price);
    return BUY;
  }
  else if (predicted_price < current_price)
  {
    log(SELL, predicted_price);
    return SELL;
  }

  return WAIT;
}

void Exchange::log(enum Trade order_type, double predicted_price)
{
  std::cout << "Predicted Price: " << predicted_price << std::endl;

  if (order_type == BUY)
  {
    std::cout << "Buy Order Ready" << std::endl;
  }
  else if (order_type == SELL)
  {
    std::cout << "Sell Order Ready" << std::endl;
  }
}
