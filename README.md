Farukon is event driven backtester.

User guide

Farukon works in several modes:

Flag -m --mode optimize

Example:
python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m optimize

Launch farukon in parameter optimization mode:  "strat_params":{}, "pos_sizer":{}.
There are 2 types of optimization available: a complete search of all Grid_Search() parameters and the genetic algorithm Genetic_Search(). The number of processor cores to perform optimization is passed through the "workers=" parameter.
Optimization results are saved to a .csv file in the root directory of the program in the opt_results folder. 
Upon completion of the genetic algorithm, a training graph is displayed.

<img width="562" alt="Снимок экрана 2024-10-26 в 18 58 59" src="https://github.com/user-attachments/assets/95b62a80-93a1-4749-a564-07738e99245e">


Flag -m --mode visual

Example:
python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m visual
Statistical execution results are saved to the visual.csv file in the root directory of the program. 
Statistics are saved in the context of tested financial instruments + general aggregated statistics. And they look like:

<img width="617" alt="Снимок экрана 2024-10-27 в 20 22 19" src="https://github.com/user-attachments/assets/2beea490-b45e-41ee-a50c-de43bab4921f">

The set of indicators included in the strategy statistics is implemented in the performance.py file. TODO: add help on statistical indicators.

Upon completion of the program, a graph of profitability and drawdown is displayed.

<img width="1220" alt="Снимок экрана 2024-10-27 в 20 37 31" src="https://github.com/user-attachments/assets/347947b4-680d-46ec-9e56-50b0a951b82c">


Flag -f --folder

Specify the path to the folder with historical data on the instruments being tested. For csv files, you must specify the format of the file fields:

data_parser_params = {

        "separator": ',',               # Data series separator
        "dtformat": "%Y%m%d",           # Date format
        "tmformat": "%H%M%S",           # Time format
        "headers": 0,                   # Does our data contain a header? 0 - no, 1 - the first row is the header
        "date": 0,                      # First data column = Date
        "time": 1,                      # Second data column = Time
        "open": 2,                      # Third column of data = Open
        "high": 3,                      # Fourth column of data = High
        "low": 4,                       # Fifth data column = Low
        "close": 5,                     # Sixth data column = Close
        "vol": 6,                       # Seventh column of data
        "oi": -1,                       # Open interest data is not on file if == -1
        "timeframe": "min",             # timframe of input data
        "timeframebars": 1
    }


Flags -t --timeframe and -c --compression

Compress candles in files with historical data to the specified compression + timeframe value.

Example: python farukon.py -f .\Tickers\Si\ -t min -c 4 -sm min -m optimize

will compress 1 minute source data (see data_parser_params above) to a 4 minute timeframe.

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








