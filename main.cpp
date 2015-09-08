// Fully connected, implicit, forward neural network

#include <chrono>
#include <thread>

#include "exchange.h"
#include "net.h"
#include "training.h"

double Neuron::eta_ = 0.05;	// overall net training rate, [ 0.0...1.0 ]
double Neuron::alpha_ = 0.5;	// multiplier of last deltaWeight, [ 0.0...n ]
/*
eta = overall net learning rate
0.0 = slow learner
0.2 = medium learner
1.0 = reckless learner

alpha = momentum
0.0 = no momentum
0.5 = moderate momentum
*/

int main()
{
  const unsigned input_num = subset_length;
  const unsigned hidden_1_num = subset_length * 3;
  const unsigned hidden_2_num = subset_length * 2;
  const unsigned hidden_3_num = subset_length;
  const unsigned output_num = 1;

  unsigned topology[] = { input_num, hidden_1_num, hidden_2_num, hidden_3_num, output_num };
  unsigned topology_length = sizeof(topology) / sizeof(topology[0]);  // unsigned == 4 bytes, topology == 12 (3 variables of unsigned type), topolopy[0] == 4; 12 / 4 == 3

  Exchange Ex;
  TrainingData Training(topology_length);
  Net Net(topology, topology_length);

  double subset_inputs[input_num];
  double subset_targets[output_num];
  double neural_net_outputs[output_num];

  while (true)
  {
    int target_index = subset_length;

    Training.ImportNewRecords();

    while (!Training.TrainingComplete(target_index))
    {
      assert(Training.GetTrainingSet(subset_inputs, subset_targets, TRAINING) == topology[0]);
      Net.FeedForward(subset_inputs, subset_length);
      Net.GetResults(neural_net_outputs);
      assert(output_num == topology[topology_length - 1]);
      Net.BackProp(subset_targets);
      ++target_index;
    }

    std::cout << "Training error rate: " << Net.get_recent_average_error_() << std::endl;

    assert(Training.GetTrainingSet(subset_inputs, subset_targets, PREDICTION) == topology[0]);

    Net.FeedForward(subset_inputs, subset_length);
    Net.GetResults(neural_net_outputs);

    // Denormalized form of the last price in the current subset
    double current_price = Training.Denormalize(subset_inputs[subset_length - 1]);

    // Denormalized form of the price predicted by the neural network
    double predicted_price = Training.Denormalize(neural_net_outputs[0]);

    // Stores value that is representative of the action to be taken based on the current price and the predicted price
    int order_type = Ex.GetTrade(current_price, Training.Denormalize(neural_net_outputs[0]));

    // The error rate of the neural network as it trained to predict known targets
    double err_rate = Net.get_recent_average_error_();

    Ex.StoreOutput(current_price, predicted_price, Trade(order_type), err_rate);

    std::cout << "Waiting for new training data   ";
    int ms = 50;

    int last_db_row = Training.Get_db_row_count();

    // Delays execution until a new record is detected in input.sqlite
    while (last_db_row == Training.Get_db_row_count())
    {
      std::cout << "\b\\" << std::flush;
      std::this_thread::sleep_until(std::chrono::system_clock::now() + std::chrono::milliseconds(ms));
      std::cout << "\b|" << std::flush;
      std::this_thread::sleep_until(std::chrono::system_clock::now() + std::chrono::milliseconds(ms));
      std::cout << "\b/" << std::flush;
      std::this_thread::sleep_until(std::chrono::system_clock::now() + std::chrono::milliseconds(ms));
      std::cout << "\b-" << std::flush;
      std::this_thread::sleep_until(std::chrono::system_clock::now() + std::chrono::milliseconds(ms));
    }
    std::cout << std::endl;

    Ex.Set_last_price_(Training.Denormalize(neural_net_outputs[0]));

    Training.GetTrainingSet(subset_inputs, subset_targets, UPDATE);
    Net.BackProp(subset_targets);

    Training.Reset();
  }

  return 0;
}

/*
todo
  wait until n records are known before trying to predict the price after m future trades instead of simply predicting the next record to arrive
  predicted future price after m trades, if the total volume of m trades exceeds predefined threshold, will get inserted into output db regardless of profit margin, trader.py determines whether to act on that output db record or not
  after completing the above, neural net to new folder and experiment with adding additional hidden layers and using a different transform function
*/
