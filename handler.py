#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse

def args_parser():
    parser = argparse.ArgumentParser(description="Flags of Command-Line options")
    parser.add_argument(
        "-f", "--folder",                                         # указывающий путь к папке с данными
        default='',                                         # Значение по умолчанию
        required=True,                                     # Необязательный параметр
        type=str,                                           # Тип строковый
        help="Path to folder with data"
    )
    parser.add_argument(
        "-t", "--timeframe",
        default="min",
        required=True,
        type=str,
        choices=["min", "d", "w", "m", "y"],
        help="min - Minutes, d - Daily, w - Weekly, m - Month, y - Year"
    )
    parser.add_argument(                                    # Создаем аргумент
        "-c", "--compression",                                    # указывающий на сколько нужно зжать минутные свечи
        default=1,                                          # Значение по умолчанию
        required=True,                                     # Необязательный параметр
        type=int,                                           # Тип целочисленный
        help="Compress to required timeframe. All data has 1 minute time frame by default. Example: for 5 minutes timeframe use --compression 5."
    )
    return parser.parse_args()