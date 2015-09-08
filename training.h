#ifndef TRAINING_H
#define TRAINING_H

#include <iostream>
#include <deque>
#include <sstream>
#include <string>
#include <limits>		// numeric_limits<double>::max, numeric_limits<double>::min
#include <chrono>		// system_clock::now, seconds
#include <thread>		// sleep_until
#include "sqlite3.h"

enum RoundType { TRAINING, PREDICTION, UPDATE };
const static unsigned subset_length = 33;

class TrainingData
{
public:
  TrainingData(unsigned total_layers);
  bool TrainingComplete(unsigned target_index);
  void ImportNewRecords();
  void RemoveOldRecords();

  unsigned GetTrainingSet(double subset_inputs[], double subset_targets[], enum RoundType round_flag);
  void Normalize(unsigned set_size);
  double Denormalize(double target_value);

  unsigned Get_db_row_count();
  void Reset();

private:
  static int TrainingCallback(void *NotUsed, int argc, char **argv, char **azColName);
  static int RowCountCallback(void *NotUsed, int argc, char **argv, char **azColName);

  static std::deque<double> input_data;

  static double subset_data_[subset_length + 1];
  static unsigned db_row_count_;

  int offset_ = 0;

  static double subset_min_;
  static double subset_max_;
  const int range_min_ = -1;
  const int range_max_ = 1;

  int rc_;
  sqlite3 *input_db_;
  const char* input_data_file_ = "/home/evan/hdd1/programming/git_repos/neural-network-trading-bot/data/input.sqlite";	// change this to your local path to input.sqlite
  const std::string input_data_table_ = "trade_data";
  char *z_err_msg_ = 0;
  const int input_db_timeout = 5000;
};

#endif
