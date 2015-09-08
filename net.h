#ifndef NET_H
#define NET_H

#include <cassert>
#include <cmath>
#include <iostream>

#include "neuron.h"

class Net
{
public:
  Net(unsigned const topology[], unsigned const topologySize);
  void FeedForward(double subset_inputs[], unsigned subset_length);
  void GetResults(double neural_net_outputs[]);
  void BackProp(double subset_targets[]);
  double get_recent_average_error_(void) const;
private:
  std::vector<Layer> layers_;
  double accumulated_error_;
  double recent_average_error_;
  double recent_average_smoothing_factor_;
};

#endif // NET_H
