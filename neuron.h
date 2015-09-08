#ifndef NEURON_H
#define NEURON_H

#include <vector>
#include "connection.h"

class Neuron;
typedef std::vector<Neuron> Layer;

class Neuron
{
public:
  Neuron(unsigned layer_outputs, unsigned neuron_num);
  void Set_neuron_output_value_(double value);
  double Get_neuron_output_value_(void) const;

  void FeedForward(const Layer &PreviousLayer);
  void CalcOutputGradient(double target_value);
  void CalcHiddenGradient(const Layer &NextHiddenLayer);
  void UpdateInputWeight(Layer &PreviousLayer);
private:
  static double TransferFunction(double x);
  static double TransferFunctionDerivative(double x);
  static double RandomWeight(void);

  double SumDOW(const Layer &NextHiddenLayer) const;

  static double eta_;
  static double alpha_;
  double neuron_output_value_;
  std::vector<Connection> output_weights_;

  unsigned neuron_number_;
  double gradient_;
};

#endif
