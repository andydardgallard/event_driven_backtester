#!/usr/bin/python
# -*- coding: utf-8 -*-

from data import CustomCSVDataHandler, CustomCSVDataExecutor
from queue import Queue
from handler import args_parser
import time
from stratagy import Stratagy
from event import Event, SignalEvent
import datetime as dt
from backtest import Backtest
from execution import SimulatedExecutionHandler
from portfolio import Portfolio
from itertools import product
import numpy as np
from concurrent.futures import ProcessPoolExecutor

class MovingAverageCrossStratagy(Stratagy):
    def __init__(self, bars: CustomCSVDataExecutor, events: Queue, short_window=None, long_window=None) -> None:
        super().__init__()
        self.__bars = bars
        self.__symbol_list = self.__bars.get_symbol_list
        self.__events = events
        self.__short_window = short_window
        self.__long_window = long_window
        self.__bought = self._calculate_initial_bought()       
    
    @property
    def get_short_window(self) -> int:
        return self.__short_window

    @get_short_window.setter
    def set_short_window(self, short_window: int) -> None:
        self.__short_window = short_window
    
    @property
    def get_long_window(self) -> int:
        return self.__long_window

    @get_long_window.setter
    def set_long_window(self, long_window: int) -> None:
        self.__long_window = long_window

    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list

    @property
    def get_bought(self) -> dict:
        return self.__bought
    
    def _calculate_initial_bought(self):
        bought = {}
        for symbol in self.get_symbol_list:
            bought[symbol] = "OUT"
        return bought

    def calculate_signals(self, event: Event, short_window, long_window):
        self.set_short_window = short_window
        self.set_long_window = long_window
        event_name = event.get_event_type
        if event_name == "MARKET":
            for symbol in self.get_symbol_list:
                bars = self.__bars.get_latest_bars_value(symbol, "close", self.get_long_window)
                bar_date = self.__bars.get_latest_bar_datetime(symbol)
                if bars is not None and bars.size >= self.get_long_window:
                    short_sma = np.mean(bars[-self.get_short_window:])
                    long_sma = np.mean(bars[-self.get_long_window:])
                    dt_ = bar_date
                    signal_direction = ""
                    if short_sma > long_sma and self.get_bought[symbol] == "OUT":
                        signal_direction = "LONG"
                        signal = SignalEvent(1, symbol, dt_, signal_direction, 1.0)
                        self.__events.put(signal)
                        self.get_bought[symbol] = signal_direction
                    elif short_sma < long_sma and self.get_bought[symbol] == "LONG":
                        signal_direction = "EXIT"
                        signal = SignalEvent(1, symbol, dt_, signal_direction, 1.0)
                        self.__events.put(signal)
                        self.get_bought[symbol] = "OUT"    

def optimization(*params_list):
    initial_capital = 1_000_000.0
    heartbeat = 0.0
    start_date = dt.datetime(2010, 1, 1, 0, 0, 0)
    strat_params_list = (params_list[0][0], params_list[0][1])
    data_iter = params_list[0][2]
    symbol_list = list(params_list[0][2].keys())
    backtest = Backtest(
        data_iter,
        symbol_list,
        initial_capital,
        heartbeat,
        start_date,
        CustomCSVDataExecutor,
        SimulatedExecutionHandler,
        Portfolio,
        MovingAverageCrossStratagy,
        strat_params_list
    )
    backtest.simulate_trading_opt()

if __name__ == "__main__":
    start_time = time.time()
    #create datafeed
    args = args_parser()
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
        "timeframe": "min",
        "timeframebars": 1
    }
    symbol_list = ["Si-12.20.txt", "Si-3.20.txt", "Si-9.20.txt", "Si-6.20.txt"]
    data = CustomCSVDataHandler(
        args.folder, 
        data_parser_params, 
        args.timeframe, 
        args.compression,
        symbol_list)
    data_iter = data()

    short_sma_window = [100, 150, 200]
    long_sma_window = [500, 750, 1_000]
    strat_params = list(product(short_sma_window, long_sma_window))
    strat_params_list = []
    for item in strat_params:
        strat_params_list.append((item[0], item[1], data_iter))
    
    with ProcessPoolExecutor(max_workers=7) as executor:
        results = (executor.map(optimization, strat_params_list))

    end_time = time.time()
    print(f"Elapsed_time= {end_time - start_time}")
