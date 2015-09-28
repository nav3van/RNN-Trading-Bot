# Neural Network Trading Bot
## About
C++ implementation of artificial neural network (ann) that analyzes BTC-e trade data to predict future 
prices and generate trades accord to those predictions. Uses python3 to executes trades output 
by the neural network on the BTC-e exchange.

##### trade_stream.py 
--- Sends HTTP request to BTC-e public API every 2 seconds to gather recent trade data

##### trading_floor.py
--- Checks output.sqlite for new records inserted by neural-network-predictor and executes orders to BTC-e if various criteria are met

##### ann-predictor
--- Inserts records into output.sqlite containing the current price, predicted price, and type of trade to execute 

## Neural Network Configuration
| File       | Variable      | Range     | Description                                |
| :--------- | ------------- | :-------- | :----------------------------------------- |
| main.cpp   | eta_          | 0.0...1.0 | Overall net training rate                  |
| main.cpp   | alpha_        | 0.0...n   | Momentum multiplier                        |
| main.cpp   | topology      | n/a       | Defines number of node per layer           |
| training.h | subset_length | n/a       | Defines number of records per training set |

## Usage
'''
$ mkdir build
$ cd build
$ cmake .. && make
$ ./ann_predictor
'''
'''
$ python3 pyTrader/trade_stream.py
'''
'''
$ python3 pyTrader/trading_floor.py
'''

- trade_stream.py, trading_floor.py, and ann-predictor all must be run in separate terminal windows
- Execute programs in following order: ann-predictor, trade_stream.py, trading_floor.py
- neural-network-predictor will automatically proceed with execution when subset_length * 10 records are present in input.sqlite
- trading_floor.py will automatically proceed with execution once records are present in output.sqlite