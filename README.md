Farukon is event driven backtester.

User guide

Farukon works in several modes:

Flag -m --mode optimize

All necessary strategy parameters are specified in a separate class. In Example Stratagy1. All strategies are considered as part of the overall portfolio. Even if one strategy is used.

self.__params = {

            "stratagy": PriceChannel,                           # Pointer to stratagy. Subclass of Stratagy.py class
            "stratagy_weight": 0.5,                             # Weight stratagy in portfolio
            "symbol_base_name": "Si",                           # Name of underlying asset
            "symbol_list": ["Si-6.24.txt", "Si-9.24.txt"],      # list of symbols
            "strat_params": {                                   # Stratagy parameters
                "avg_price_period": [16],                       # Single value for visualization
                "channel_period": [215],
                # "avg_price_period": np.arange(2, 21, 1),      # Range for optimization
                # "channel_period": np.arange(50, 1000, 5),
                },
            "pos_sizer": {                                      # Possizer parameters
                "pos_sizer_type": ["mpr"],
                "pos_sizer_value": [1.5],
                # "pos_sizer_value": np.arange(0.25, 2.25, 0.25)
                },
            "margin_params": {                                  # Margin plan parameters from broker
                "min_margin": 0.5,
                "marginCall_type": "close_deal", #stop - stop trading, close-deal - close current deal and continue trading
                },
            "args": {                                          
                "folder": "Tickers/Si",                         # Folder path of Tickers
                "timeframe": "min",
                "compression": 4,
                },
            "data_parser_params": {
                "separator": ',',                               # Separator
                "dtformat": "%Y%m%d",                           # Date format
                "tmformat": "%H%M%S",                           # Time format
                "headers": 0,                                   # Headers in data files: number of row 
                "date": 0,                                      # First column = Date
                "time": 1,                      
                "open": 2,                      
                "high": 3,                      
                "low": 4,                       
                "close": 5,                     
                "vol": 6,                       
                "oi": -1,                                       # There is no column with Open Interest
                "timeframe": "min",                             # Timeframe of input data
                "timeframebars": 1,
                },
            "ga_params" : {                                     # Parameters of Genetic Algorythm
                "population_size": 5,
                "p_crossover": 0.8,
                "p_mutation": 0.2,
                "max_generations": 5,
                "fitness_direction": "max",
                # "fitness_value": "APR/DD_factor",
                "fitness_value": "recovery_factor",
                # "fitness_value": "profit_factor",
                # "fitness_value": "win_rate"
            }

Example:
python farukon.py -f -sm min -m optimize

Launch farukon in parameter optimization mode:  "strat_params":{}, "pos_sizer":{}.
There are 2 types of optimization available: a complete search of all Grid_Search() parameters and the genetic algorithm Genetic_Search(). The number of processor cores to perform optimization is passed through the "workers=" parameter.
Optimization results are saved to a .csv file in the root directory of the program in the opt_results folder. 
Upon completion of the genetic algorithm, a training graph is displayed. Example for two stratagies with diffrent fitness values. x axis - number of generations.

<img width="1398" alt="Снимок экрана 2024-11-10 в 23 43 04" src="https://github.com/user-attachments/assets/127928ae-8de7-4955-ad4b-032c55e14ef4">



Flag -m --mode visual

Example:
python farukon.py -f -sm min -m visual
Statistical execution results are saved to the visual.csv file in the root directory of the program. 
Statistics are saved in the context of tested financial instruments + general aggregated statistics. And they look like:

<img width="617" alt="Снимок экрана 2024-10-27 в 20 22 19" src="https://github.com/user-attachments/assets/2beea490-b45e-41ee-a50c-de43bab4921f">

The set of indicators included in the strategy statistics is implemented in the performance.py file. TODO: add help on statistical indicators.

Upon completion of the program, a graph of profitability and drawdown is displayed for every stratagy in portfolio.

<img width="1395" alt="Снимок экрана 2024-11-10 в 23 48 35" src="https://github.com/user-attachments/assets/96f4e77f-fe08-4f09-9da3-9c537456ff74">

And entirely for the portfolio as a whole.

<img width="1402" alt="Снимок экрана 2024-11-10 в 23 50 10" src="https://github.com/user-attachments/assets/8da8895f-ba09-438c-a3e3-25e084ce6b71">

And correlation matrix of stratagies in portfolio.

<img width="1396" alt="Снимок экрана 2024-11-10 в 23 51 22" src="https://github.com/user-attachments/assets/de8ee193-03d0-4d21-9e4e-4301a2ca5b46">



Flag -sm --stats_mode 

Accepted values ​​are min and full. Display of statistical results: minimum or full sets.



Once the main optimizer has completed its work, you can run the auxiliary script for processing the obtained results opresults_handler.py:

Example:
python.exe .\optresults_handler.py -f .\opt_results\SYMI_Ch_SMA_up_5min.csv -d 2D -y set -x mpr -m visual

Flag -f --file path to the file with processed optimization results

Flag -m --mode: visual or select

Visual mode works simultaneously with flags: 

-d --dimension: accepts "2D" or "3D" values

-x --xaxis: x-axis values

-y --yaxis: y axis value

Example: python .\optresults_handler.py -f .\opt_results\Price_Channel_5min.csv -d 2D -y recovery_factor -x mpr -m visual

<img width="555" alt="Снимок экрана 2024-10-27 в 21 08 59" src="https://github.com/user-attachments/assets/1170a61e-3e09-4ff4-9943-212673b2f27b">


If you pass the value "set" as the value of the -y --yaxis flag, then the set of indicators listed in the parameter will be displayed

results_scope = {

    "APR/DD_factor": {"value": 4, "optim": "max"},
    "DD_pcr": {"value": 0.25, "optim": "min"},
    "recovery_factor":  {"value": 5, "optim": "max"},
    "profit_factor": {"value": 2, "optim": "max"},
    "expected_payoff_probability": {"value": 0, "optim": "max"},
    "breakeven_tradeoff": {"value": 0, "optim": "max"},
    "sharp_ratio": {"value": 0.1, "optim": "max"},
    "APR": {"value": 0, "optim": "max"},
    "deals_count": {"value": 12, "optim": "max"},
}


<img width="1218" alt="Снимок экрана 2024-10-27 в 21 14 24" src="https://github.com/user-attachments/assets/e072509b-db73-4a8f-8013-b3b98b96c1cd">


The select mode selects optimization results that correspond to the values ​​of the "results_scope" parameter (see above). Where the "optim" parameter is responsible for the direction of optimization, and the "value" parameter is responsible for the threshold value. The result is saved to the file select.csv in the root directory.








