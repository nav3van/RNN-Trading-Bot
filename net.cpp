#include "net.h"

// Post Conditions
// - A vector of neurons has been created for each layer of the neural net
// - Each neuron is connected to all neurons in the following layer so its output is the next layer neurons input, except for the last layer which has no ouput
// - Each neuron in each layer knows how many outputs it has and its position within its own layer
// - Last neuron created for each layer is initialized to 1.0 since those are bias neurons
Net::Net(unsigned const topology[], unsigned const topology_length)
{
  unsigned total_layers = topology_length;

  for (int current_layer = 0; current_layer < total_layers; ++current_layer)
  {
    // initialize a new vector of neurons for each layer
    layers_.emplace_back();

    unsigned current_layer_outputs;

    // if: the loop is on the final layer there are no outputs
    // else: current_layer_outputs is equal to the number of neurons in the next layer
    if (current_layer == topology_length - 1)
    {
      current_layer_outputs = 0;
    }
    else
    {
      current_layer_outputs = topology[current_layer + 1];
    }

    // for each neurons in the current layer of the loop, tell that neuron how many outputs it needs to have and that neurons position in the current layer
    for (int current_neuron = 0; current_neuron <= topology[current_layer]; ++current_neuron)
    {
      layers_.back().push_back(Neuron(current_layer_outputs, current_neuron));
    }

    // force the bias neuron (last neuron created for each layer) to have an ouput initially set to 1.0
    // layers_.back() == last layer initialized at this point in the loop
    // layers_.back().back() == last initialized neuron in that layer
    layers_.back().back().Set_neuron_output_value_(1.0);
  }
}

void Net::FeedForward(double subset_inputs[], unsigned subset_length)
{
  // set output for each neuron in layer 1 to be a value from inputVals[]
  for (int current_neuron = 0; current_neuron < subset_length; ++current_neuron)
  {
    layers_[0][current_neuron].Set_neuron_output_value_(subset_inputs[current_neuron]);
  }

  // Forward propogation
  for (int current_layer = 1; current_layer < layers_.size(); ++current_layer)
  {
    Layer &PreviousLayer = layers_[current_layer - 1];

    for (int current_neuron = 0; current_neuron < layers_[current_layer].size() - 1; ++current_neuron)
    {
      layers_[current_layer][current_neuron].FeedForward(PreviousLayer);
    }
  }
}

void Net::GetResults(double neural_net_outputs[])
{
  for (int current_neuron = 0; current_neuron < layers_.back().size() - 1; ++current_neuron)
  {
    // get the output value for each neuron in the last layer and insert it into resultVals
    neural_net_outputs[current_neuron] = layers_.back()[current_neuron].Get_neuron_output_value_();
  }
}

void Net::BackProp(double subset_targets[])
{
  // Calculate overall net error (RMS(root mean square error) of output neuron errors
  // the error metric is what the back propogation algorithm will try to minimize and indicates whether the training is working or not

  Layer &OutputLayer = layers_.back();
  accumulated_error_ = 0.0;

  for (int current_neuron = 0; current_neuron < OutputLayer.size() - 1; ++current_neuron)
  {
    double delta = subset_targets[current_neuron] - OutputLayer[current_neuron].Get_neuron_output_value_();
    accumulated_error_ += delta * delta;
  }

  accumulated_error_ /= OutputLayer.size() - 1;
  accumulated_error_ = sqrt(accumulated_error_);

  // implement a recent average measurement to let us know how well the net is being trained
  recent_average_error_ = (recent_average_error_ * recent_average_smoothing_factor_ + accumulated_error_) / (recent_average_smoothing_factor_ + 1.0);

  // Calculate gradients for each neuron in last layer
  for (int current_neuron = 0; current_neuron < OutputLayer.size() - 1; ++current_neuron)
  {
    OutputLayer[current_neuron].CalcOutputGradient(subset_targets[current_neuron]);
  }

  // Starting with the last hidden layer working backwards toward the first hidden layer
  for (int current_hidden_layer = layers_.size() - 2; current_hidden_layer > 0; --current_hidden_layer)
  {
    Layer &CurrentHiddentLayer = layers_[current_hidden_layer];
    Layer &NextHiddenLayer = layers_[current_hidden_layer + 1];

    // Calculate gradients for each neuron in the currentHidden layer
    for (int current_hidden_neuron = 0; current_hidden_neuron < CurrentHiddentLayer.size(); ++current_hidden_neuron)
    {
      CurrentHiddentLayer[current_hidden_neuron].CalcHiddenGradient(NextHiddenLayer);
    }
  }

  // For all layers starting with the last layer and working backwards toward the second layer (don't need first layer since no weights are coming into it)
  for (int current_layer = layers_.size() - 1; current_layer > 0; --current_layer)
  {
    Layer &CurrentLayer = layers_[current_layer];
    Layer &PreviousLayer = layers_[current_layer - 1];

    // Update connection weights for each neuron in currentLayer
    for (int current_neuron = 0; current_neuron < CurrentLayer.size() - 1; ++current_neuron)
    {
      CurrentLayer[current_neuron].UpdateInputWeight(PreviousLayer);
    }
  }
}

double Net::get_recent_average_error_(void) const
{
  return recent_average_error_;
}
