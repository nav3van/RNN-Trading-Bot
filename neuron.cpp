#include "neuron.h"

#include <cmath>	// tanh()
#include <random>   // random_device, mt19937, uniform_real_distribution
#include <iostream>

// Post condition:
// Current layer neuron has a connection initialized to every neuron in the next layer
// Each connection is set to have a random weight between 0.0 and 1.0
// Current layer neuron knows its neuronID for the layer it resides
Neuron::Neuron(unsigned layer_outputs, unsigned neuron_num)
{
  for (int current_neuron_output = 0; current_neuron_output < layer_outputs; ++current_neuron_output)
  {
    output_weights_.emplace_back();
    output_weights_.back().connection_weight = RandomWeight();
  }
  neuron_number_ = neuron_num;
}

void Neuron::Set_neuron_output_value_(double value)
{
  neuron_output_value_ = value;
}

double Neuron::Get_neuron_output_value_(void) const
{
  return neuron_output_value_;
}

void Neuron::FeedForward(const Layer &PreviousLayer)
{
  double sum = 0.0;

  // For each neuron in the previous layer, multiply it's output by the random weight of the connection to the current layer neuron and add the amount to sum
  for (int current_neuron = 0; current_neuron < PreviousLayer.size(); ++current_neuron)
  {
    sum += PreviousLayer[current_neuron].Get_neuron_output_value_() * PreviousLayer[current_neuron].output_weights_[neuron_number_].connection_weight;
  }

  // The output of the current layer neuron is set equal to the hyperbolic tangent of sum
  neuron_output_value_ = Neuron::TransferFunction(sum);
}

// Post condition
// delta set to the difference between the neuron's computed value and the expected value
// gradient set to the delta value multipled by the derivative of the hyperbolic tangent
void Neuron::CalcOutputGradient(double target_value)
{
  double delta = target_value - neuron_output_value_;
  gradient_ = delta * Neuron::TransferFunctionDerivative(neuron_output_value_);
}

void Neuron::CalcHiddenGradient(const Layer &NextHiddenLayer)
{
  double dow = SumDOW(NextHiddenLayer);
  gradient_ = dow * Neuron::TransferFunctionDerivative(neuron_output_value_);
}

void Neuron::UpdateInputWeight(Layer &PreviousLayer)
{
  // The weights to be updated are in the Connection container in the neurons in the preceding layer
  for (unsigned current_previous_layer_neuron = 0; current_previous_layer_neuron < PreviousLayer.size(); ++current_previous_layer_neuron)
  {
    Neuron &Neuron = PreviousLayer[current_previous_layer_neuron];
    double old_delta_weight = Neuron.output_weights_[neuron_number_].connection_delta_weight;

    // individual input, magnified by the gradient and train rate + momentum (a fraction of the old delta weight)
    double new_delta_weight = eta_ * Neuron.Get_neuron_output_value_() * gradient_ + alpha_ * old_delta_weight;

    Neuron.output_weights_[neuron_number_].connection_delta_weight = new_delta_weight;
    Neuron.output_weights_[neuron_number_].connection_weight += new_delta_weight;
  }
}

double Neuron::TransferFunction(double x)
{
  // hyperbolic tangent function; tanh - output range[ -1.0...1.0 ]
  // when setting up training data, need to make sure that the output data is within the range of what the transfer function is able to make
  return tanh(x);
}

double Neuron::TransferFunctionDerivative(double x)
{
  // tanh derivative
  return 1.0 - x * x;	// fast approximation of the derivative of the hyperbolic tangent
}

double Neuron::SumDOW(const Layer &NextHiddenLayer) const
{
  double sum = 0.0;

  // Sum our contribution of the errors at the node we feed
  for (int current_neuron = 0; current_neuron < NextHiddenLayer.size() - 1; ++current_neuron)
  {
    sum += output_weights_[current_neuron].connection_weight * NextHiddenLayer[current_neuron].gradient_;
  }
  return sum;
}

double Neuron::RandomWeight(void)
{
  std::random_device rd;
  std::mt19937 generator(rd());
  std::uniform_real_distribution<double> distribution(0.0, 1.0);
  double multiplier = distribution(generator);
  double random_weight = generator()*multiplier / generator.max()*multiplier;

  return random_weight;
}
