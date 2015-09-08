#include "training.h"

std::deque<double> TrainingData::input_data = {};
double TrainingData::subset_data_[subset_length + 1];
unsigned TrainingData::db_row_count_;
double TrainingData::subset_min_ = std::numeric_limits<double>::max();
double TrainingData::subset_max_ = std::numeric_limits<double>::min();

// Post Conditions
// - input.sqlite is opened
// - input.sqlite contains a record count >= 10*subset_length
TrainingData::TrainingData(unsigned total_layers)
{
  rc_ = sqlite3_open(input_data_file_, &input_db_);

  if (rc_ != SQLITE_OK)
  {
    std::cout << "SQL error: " << z_err_msg_ << std::endl;
    sqlite3_free(z_err_msg_);
  }

  while (Get_db_row_count() <= subset_length * 10)
  {
    double numerator = db_row_count_;
    double denominator = (subset_length * 10) + 1.0;
    std::cout << "\rData collection " << (numerator / denominator) * 100.0 << "% complete" << std::flush;

    // A new record will appear every 2 seconds at best since the BTC-e API updates every 2 seconds
    std::this_thread::sleep_until(std::chrono::system_clock::now() + std::chrono::seconds(2));
  }
}

// Post Conditions
// - Returns true when the last subset of the current training round includes the move recent records from input.sqlite
// - Returns false otherwise
bool TrainingData::TrainingComplete(unsigned target_index)
{
  if (target_index == input_data.size())
  {
    return true;
  }

  return false;
}

// Post Conditions
// - All new records that have been inserted to input.sqlite since the prior training round have been added to input_data
void TrainingData::ImportNewRecords()
{
  if (rc_)
  {
    std::cout << "Cannot open database, unable to import: " << sqlite3_errmsg(input_db_) << std::endl;
    exit(0);
  }
  else
  {
    std::string sql_string = "SELECT timestamp FROM " + input_data_table_ + " LIMIT -1 OFFSET " + std::to_string(input_data.size()) + ";";
    const char* sql = sql_string.c_str();

    sqlite3_busy_timeout(input_db_, input_db_timeout);
    rc_ = sqlite3_exec(input_db_, sql, TrainingCallback, 0, &z_err_msg_);

    if (rc_ != SQLITE_OK)
    {
      fprintf(stderr, "SQL error: %s\n", z_err_msg_);
      sqlite3_free(z_err_msg_);
    }
  }
}

// Once the record count of input_data exceeds a predefined length, remove old records to maintain constant deque size
// Old records will throw off predictions eventually as the current market conditions will render old records useless
void TrainingData::RemoveOldRecords()
{
  if (input_data.size() > subset_length * 12)
  {
    unsigned trim_range = (subset_length * 12) - (subset_length * 10);

    for (unsigned i = 0; i < trim_range; ++i)
    {
      std::cout << input_data[i] << " removed" << std::endl;
      input_data.pop_front();
    }
  }
}

int TrainingData::TrainingCallback(void *NotUsed, int argc, char **argv, char **azColName)
{
  for (int x = 0; x < argc; ++x)
  {
    double data_record;
    std::stringstream ss(argv[x]);
    ss >> data_record;
    input_data.push_back(data_record);
  }

  return 0;
}

unsigned TrainingData::GetTrainingSet(double subset_inputs[], double subset_targets[], enum RoundType round_flag)
{
  unsigned set_size;

  // PREDICTION rounds have no target since the target is unknown and therefore should not be accounted for when retrieving the current set from input_data
  // TRAINING rounds have a target so they need to account for it by retrieving 1 element from input_data
  if (round_flag == PREDICTION)
  {
    set_size = subset_length;
  }
  else
  {
    set_size = subset_length + 1;
  }

  // Extract subset of input_data to use as the current training set
  for (unsigned x = 0; x < set_size; ++x)
  {
    // Prevents attempted retrieval from a non-existant input_data index
    if (x + offset_ != input_data.size())
    {
      subset_data_[x] = input_data[x + offset_];
    }
  }

  Normalize(set_size);

  // Set first subset of input_data_ equal to subset_inputs
  for (unsigned y = 0; y < subset_length; ++y)
  {
    subset_inputs[y] = subset_data_[y];
  }

  // TRAINING rounds have a known target that needs to be stored in subset_targets for later use
  // offset_ needs to increment so next training subset starts 1 index ahead of the current subset
  // should not increment for a PREDICTION round as it is using the final subset elements from input_data
  if (round_flag == TRAINING)
  {
    subset_targets[0] = subset_data_[subset_length];
    ++offset_;
  }

  return ((sizeof(subset_data_) / sizeof(subset_data_[0])) - 1);
}

// Normalizes the values within the current subset
void TrainingData::Normalize(unsigned set_size)
{
  for (unsigned x = 0; x < set_size; ++x)
  {
    if (subset_data_[x] > subset_max_)
    {
      subset_max_ = subset_data_[x];
    }
    if (subset_data_[x] < subset_min_)
    {
      subset_min_ = subset_data_[x];
    }
  }
  for (unsigned y = 0; y < set_size; ++y)
  {
    subset_data_[y] = (((subset_data_[y] - subset_min_) * (range_max_ - range_min_)) / (subset_max_ - subset_min_)) + range_min_;
  }
}

// Takes a normalized value from the current subset as argument and returns the denormalized equivalent
double TrainingData::Denormalize(double target_value)
{
  return (((subset_min_ - subset_max_) * target_value - (range_max_ * subset_min_) + (subset_max_ * range_min_)) / (range_min_ - range_max_));
}

// Returns the current number of rows present in input.sqlite
unsigned TrainingData::Get_db_row_count()
{
  if (rc_)
  {
    std::cout << "Cannot open database, unable to count records: " << sqlite3_errmsg(input_db_) << std::endl;
    exit(0);
  }
  else
  {
    std::string sql_string = "SELECT COUNT(*) FROM " + input_data_table_;
    const char* sql = sql_string.c_str();

    sqlite3_busy_timeout(input_db_, input_db_timeout);
    rc_ = sqlite3_exec(input_db_, sql, RowCountCallback, 0, &z_err_msg_);

    if (rc_ != SQLITE_OK)
    {
      std::cout << "SQL error: " << z_err_msg_ << std::endl;
      sqlite3_free(z_err_msg_);
    }
  }

  return db_row_count_;
}

int TrainingData::RowCountCallback(void *NotUsed, int argc, char **argv, char **azColName)
{
  for (int i = 0; i < argc; ++i)
  {
    std::stringstream ss(argv[i]);
    ss >> db_row_count_;
    ss.str("");
  }

  return 0;
}

// Resets subset_min_ and subset_max_ so that each training set can be normalized with the local minimum and maximum.
// offset_ track of the starting index of the current subset within input_data
// offset_ resets so that each training round begins training from the beginning of input_data
void TrainingData::Reset()
{
  subset_min_ = std::numeric_limits<double>::max();
  subset_max_ = std::numeric_limits<double>::min();
  offset_ = 0;
}
