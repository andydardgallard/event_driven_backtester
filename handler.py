#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os, datetime
from itertools import product

def args_parser():
    parser = argparse.ArgumentParser(description="Flags of Command-Line options")
    parser.add_argument(
        "-f", "--folder",                                    # указывающий путь к папке с данными
        default= '',                                         # Значение по умолчанию
        required= True,                                      # Необязательный параметр
        type= str,                                           # Тип строковый
        help= "Path to folder with data"
    )
    parser.add_argument(
        "-t", "--timeframe",
        default= "min",
        required= True,
        type= str,
        choices= ["min", "d", "w", "m", "y"],
        help= "min - Minutes, d - Daily, w - Weekly, m - Month, y - Year"
    )
    parser.add_argument(                                    # Создаем аргумент
        "-c", "--compression",                              # указывающий на сколько нужно зжать минутные свечи
        default= 1,                                         # Значение по умолчанию
        required= True,                                     # Необязательный параметр
        type= int,                                          # Тип целочисленный
        help= "Compress to required timeframe. All data has 1 minute time frame by default. Example: for 5 minutes timeframe use --compression 5."
    )
    parser.add_argument(
        "-sm", "--stats_mode",
        default= "min",
        required= True,
        type= str,
        choices= ["min", "full"],
        help= "min - minimal set of stratagy stats, full - max set of stratagy stats"
    )
    return parser.parse_args()

def clear_files() -> None:
    file = "opt.csv"
    if os.path.exists(file):
        os.remove(file)

def optimization_params_handler(opt_params: dict) -> list:
    indicators_params = [opt_params["strat_params"][key] for key in opt_params["strat_params"]]
    pos_sizer_params = [opt_params["pos_sizer"][key] for key in opt_params["pos_sizer"]]
    product_ = list(product(*indicators_params, *pos_sizer_params))
    params_list = []
    
    for item in product_:
        params_dict = {}
        params_dict["indicators"] = {key: item[indx] for indx, key in enumerate(opt_params["strat_params"])}
        params_dict["pos_sizers"] = {key: item[indx + len(opt_params["strat_params"])] for indx, key in enumerate(opt_params["pos_sizer"])}
        params_dict["data_iter"] = opt_params["data_iter"]
        params_dict["args"] = opt_params["args"]
        params_list.append(params_dict)
    return params_list

def resample_handler(*params) -> list:
    out = []
    if params[0]["open"] > 0:
        out.append(("open", "first"))
    if params[0]["high"] > 0:
        out.append(("high", "max"))
    if params[0]["low"] > 0:
        out.append(("low", "min"))
    if params[0]["close"] > 0:
        out.append(("close", "last"))
    if params[0]["vol"] > 0:
        out.append(("vol", "sum"))
    if params[0]["oi"] > 0:
        out.append(("oi", "sum"))
    return out

instruments_info = {
    "Si-3.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": "2020-03-19 10:00:00",
        "marginal_costs": 0
    },
    "Si-6.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": "2020-06-18 10:00:00",
        "marginal_costs": 0
    },
        "Si-12.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": 18062020,
        "marginal_costs": 0
    },
        "Si-9.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": 18062020,
        "marginal_costs": 0
    }
}

def convert_str_toDateTime(string_dateTime: str) -> datetime.datetime:
    format_ = "%Y-%m-%d %H:%M:%S"
    converted_dateTime = datetime.datetime.strptime(string_dateTime, format_)
    return converted_dateTime
