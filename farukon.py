#!/usr/bin/python
# -*- coding: utf-8 -*-

from PriceChannel import PriceChannel
import time
from handler import clear_files, args_parser
from data import CustomCSVDataHandler as dHandl
from optimiziers import Grid_Search, Genetic_Search
import numpy as np

if __name__ == "__main__":
    start_time = time.time()
    clear_files()
    args = args_parser()
    stratagy = PriceChannel
    initial_capital = 1_000_000
    data_parser_params = {
        "separator": ',',               # Разделитель рядов данных
        "dtformat": "%Y%m%d",           # Формат даты
        "tmformat": "%H%M%S",           # Формат времени
        "headers": 0,                   # Содержат ли наши данные заголовок
        "date": 0,                      # Первый столбец данных = Date
        "time": 1,                      # Второй столбец данных = Time
        "open": 2,                      # Третий столбец данных = Open
        "high": 3,                      # Четветрый столбец данных = High
        "low": 4,                       # Пятый столбец данных = Low
        "close": 5,                     # Шестой столбец данных = Close
        "vol": 6,                       # Седьмой столбец данных
        "oi": -1,                       # Данных по открытому интересу нет в файле
        "timeframe": "min",             # timframe of input data
        "timeframebars": 1
    }
    symbol_list = ["Si-6.24.txt", "Si-9.24.txt"]
    data = dHandl(
        args.folder, 
        data_parser_params, 
        args.timeframe, 
        args.compression,
        symbol_list)
    
    opt_params = {
        "strat_params": {
            "avg_price_period": [5],
            "channel_period": [90],
            # "avg_price_period": np.arange(2, 21, 1),
            # "channel_period": np.arange(200, 420, 5),
        },
        "pos_sizer": {
            "pos_sizer_type": ["mpr"],
            # "pos_sizer_value": [3.3],
            "pos_sizer_value": np.arange(0.1, 10.1, 0.1)
        },
        "data_iter": data(),
        "args": args,
        "stratagy": stratagy,
        "initial_capital": initial_capital,
        "margin_params": {
            "min_margin": 0.5,
            "marginCall_type": "close_deal", #stop - stop trading, close-deal - close current deal and continue trading
        }
    }

    ga_params = {
        "population_size": 10,
        "p_crossover": 0.8,
        "p_mutation": 0.2,
        "max_generations": 10,
        "fitness_direction": "max",
        # "fitness_value": "APR/DD_factor",
        "fitness_value": "recovery_factor",
        # "fitness_value": "profit_factor",
        # "fitness_value": "win_rate"
    }

    # optimizator = Grid_Search()
    # results = optimizator(opt_params, optimizator.get_params_creator, workers= 1)
    optimizator = Genetic_Search()
    optimizator(opt_params, ga_params, workers= 1, plot= True)
  
    end_time = time.time()
    print(f"Elapsed_time= {end_time - start_time}")