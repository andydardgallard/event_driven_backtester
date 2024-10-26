#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os, datetime

def args_parser():
    parser = argparse.ArgumentParser(description="Flags of Command-Line options")
    parser.add_argument(
        "-f", "--folder",                                   # указывающий путь к папке с данными
        default= '',                                        # Значение по умолчанию
        required= True,                                     # Необязательный параметр
        type= str,                                          # Тип строковый
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
    parser.add_argument(
        "-m", "--mode",
        default= "optimize",
        required= True,
        type= str,
        choices= ["optimize", "visual"],
        help= "optimyze - optimization mode, visual - draw pnl< drawdown etc"
    )
    return parser.parse_args()

def clear_files() -> None:
    file = "opt.csv"
    if os.path.exists(file):
        os.remove(file)

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
    "Si-9.21.txt": {
        "type": "futures",
        "margin": 4_417.03,
        "commission_type": "currency",
        "trade_from_date": "2021-06-17 07:00:00",
        "expiration_date": "2021-09-16 07:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-12.21.txt": {
        "type": "futures",
        "margin": 4_445.25,
        "commission_type": "currency",
        "trade_from_date": "2021-09-16 07:00:00",
        "expiration_date": "2021-12-16 07:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-3.22.txt": {
        "type": "futures",
        "margin": 16_585.75,
        "commission_type": "currency",
        "trade_from_date": "2021-12-16 07:00:00",
        "expiration_date": "2022-03-17 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-6.22.txt": {
        "type": "futures",
        "margin": 5_912.63,
        "commission_type": "currency",
        "trade_from_date": "2022-03-17 10:00:00",
        "expiration_date": "2022-06-16 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-9.22.txt": {
        "type": "futures",
        "margin": 9_136.5,
        "commission_type": "currency",
        "trade_from_date": "2022-06-16 10:00:00",
        "expiration_date": "2022-09-15 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-12.22.txt": {
        "type": "futures",
        "margin": 10_018.69,
        "commission_type": "currency",
        "trade_from_date": "2022-09-15 09:00:00",
        "expiration_date": "2022-12-15 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-3.23.txt": {
        "type": "futures",
        "margin": 12_003.13,
        "commission_type": "currency",
        "trade_from_date": "2022-12-15 09:00:00",
        "expiration_date": "2023-03-16 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-6.23.txt": {
        "type": "futures",
        "margin": 12_583.69,
        "commission_type": "currency",
        "trade_from_date": "2023-03-16 09:00:00",
        "expiration_date": "2023-06-15 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-9.23.txt": {
        "type": "futures",
        "margin": 14_595.32,
        "commission_type": "currency",
        "trade_from_date": "2023-06-15 09:00:00",
        "expiration_date": "2023-09-21 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-12.23.txt": {
        "type": "futures",
        "margin": 13_965.5,
        "commission_type": "currency",
        "trade_from_date": "2023-09-21 09:00:00",
        "expiration_date": "2023-12-21 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-3.24.txt": {
        "type": "futures",
        "margin": 13_861.25,
        "commission_type": "currency",
        "trade_from_date": "2023-12-21 09:00:00",
        "expiration_date": "2024-03-21 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-6.24.txt": {
        "type": "futures",
        "margin": 12_394.43,
        "commission_type": "currency",
        "trade_from_date": "2024-03-21 09:00:00",
        "expiration_date": "2024-06-20 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-9.24.txt": {
        "type": "futures",
        "margin": 13_750.68,
        "commission_type": "currency",
        "trade_from_date": "2024-06-20 10:00:00",
        "expiration_date": "2024-09-19 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
}

def convert_str_toDateTime(string_dateTime: str) -> datetime.datetime:
    format_ = "%Y-%m-%d %H:%M:%S"
    converted_dateTime = datetime.datetime.strptime(string_dateTime, format_)
    return converted_dateTime
