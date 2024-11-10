#!/usr/bin/python
# -*- coding: utf-8 -*-

from PriceChannel import PriceChannel
import time
from handler import clear_files, args_parser, stratagy_name_creator, create_stats_structe
from data import CustomCSVDataHandler as dHandl
from optimiziers import Grid_Search, Genetic_Search
import numpy as np
from plot_performance import *

class Stratagy1(object):
    def __init__(self) -> None:
        self.__params = {
            "stratagy": PriceChannel,
            "stratagy_weight": 0.5,
            "symbol_base_name": "Si",
            "symbol_list": ["Si-6.24.txt", "Si-9.24.txt"],
            "strat_params": {
                "avg_price_period": [16],
                "channel_period": [215],
                # "avg_price_period": np.arange(2, 21, 1),
                # "channel_period": np.arange(50, 1000, 5),
                },
            "pos_sizer": {
                "pos_sizer_type": ["mpr"],
                "pos_sizer_value": [1.5],
                # "pos_sizer_value": np.arange(0.25, 2.25, 0.25)
                },
            "margin_params": {
                "min_margin": 0.5,
                "marginCall_type": "close_deal", #stop - stop trading, close-deal - close current deal and continue trading
                },
            "args": {
                "folder": "Tickers/Si",
                "timeframe": "min",
                "compression": 4,
                },
            "data_parser_params": {
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
                "timeframe": "min",
                "timeframebars": 1,
                },
            "ga_params" : {
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
        }
        self.__params["stratagy_name"] = stratagy_name_creator(self.__params)

    @property
    def get_stratagy_params(self) -> dict:
        return self.__params

class Stratagy2(object):
    def __init__(self) -> None:
        self.__params = {
            "stratagy": PriceChannel,
            "stratagy_weight": 0.5,
            "symbol_base_name": "Si",
            "symbol_list": ["Si-12.23.txt", "Si-3.24.txt", "Si-6.24.txt", "Si-9.24.txt"],
            "strat_params": {
                "avg_price_period": [13],
                "channel_period": [220],
                # "avg_price_period": np.arange(2, 11, 1),
                # "channel_period": np.arange(50, 1000, 5),
                },
            "pos_sizer": {
                "pos_sizer_type": ["mpr"],
                "pos_sizer_value": [1.15],
                # "pos_sizer_value": np.arange(0.05, 0.2, 0.05)
                },
            "margin_params": {
                "min_margin": 0.5,
                "marginCall_type": "close_deal", #stop - stop trading, close-deal - close current deal and continue trading
                },
            "args": {
                "folder": "Tickers/Si",
                "timeframe": "min",
                "compression": 5,
                },
            "data_parser_params": {
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
                "timeframe": "min",
                "timeframebars": 1,
                },
            "ga_params" : {
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
        }
        self.__params["stratagy_name"] = stratagy_name_creator(self.__params)

    @property
    def get_stratagy_params(self) -> dict:
        return self.__params

if __name__ == "__main__":
    start_time = time.time()
    clear_files()
    args = args_parser()
    initial_capital = 1_000_000
    stratagy_portfolio = [Stratagy1(), Stratagy2()]

    for stratagy in stratagy_portfolio:
        data = dHandl(
                stratagy.get_stratagy_params["args"]["folder"],
                stratagy.get_stratagy_params["data_parser_params"], 
                stratagy.get_stratagy_params["args"]["timeframe"],
                stratagy.get_stratagy_params["args"]["compression"],
                stratagy.get_stratagy_params["symbol_list"])
        stratagy.get_stratagy_params["args"]["args"] = args
        stratagy.get_stratagy_params["data_iter"] = data()
        stratagy.get_stratagy_params["initial_capital"] = initial_capital
        stratagy.get_stratagy_params["stratagy_pntr"] = stratagy
    
    if args.mode == "visual":
        optimizator = Grid_Search()
        optimizator(stratagy_portfolio, optimizator.get_params_creator, workers= 7)
        curve = output_portfolio_performance(stratagy_portfolio)
        plot_portfolio_pnl_drawdowns(stratagy_portfolio, curve)
    else:
        # optimizator = Grid_Search()
        # optimizator(stratagy_portfolio, optimizator.get_params_creator, workers= 7)
        optimizator = Genetic_Search()
        optimizator(stratagy_portfolio, workers= 7, plot= True)
  
    end_time = time.time()
    print(f"Elapsed_time= {end_time - start_time}")
