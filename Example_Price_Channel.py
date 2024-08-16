#!/usr/bin/python
# -*- coding: utf-8 -*-

from stratagy import Stratagy
from data import CustomCSVDataExecutor as dExec
from data import CustomCSVDataHandler as dHandl
from queue import Queue
import time
from handler import clear_files, args_parser, optimization_params_handler, instruments_info, convert_str_toDateTime
from concurrent.futures import ProcessPoolExecutor
from backtest import Backtest
from execution import SimulatedExecutionHandler
from portfolio import Portfolio
from event import Event, SignalEvent
import numpy as np

class Example_Price_Channel(Stratagy):
    """ Just an example. Not for trade!!!"""
    def __init__(self,
                 bars: dExec,
                 events: Queue,
                 strat_params_list= None
                 ) -> None:
        super().__init__()
        self.__bars = bars
        self.__symbol_list = self.get_bars.get_symbol_list
        self.__events = events
        self.__strat_params_list = strat_params_list
        self.__bought = self._calculate_initial_bought()

        self.__high_prices = {key: [] for key in self.get_symbol_list}
        self.__low_prices = {key: [] for key in self.get_symbol_list} 
        self.__signal_name = self._calculate_initial_signal_name()
        self.__high_level = self._calculate_initial_highLevel()
        self.__low_level = self._calculate_initial_lowlevel()
        self.__signal_params = {}
    
    @property
    def get_low_level(self) -> dict:
        return self.__low_level

    @property
    def get_high_level(self) -> dict:
        return self.__high_level
    
    @property
    def get_signal_params(self) -> dict:
        return self.__signal_params

    @property
    def get_low_prices(self) -> dict:
        return self.__low_prices

    @property
    def get_high_prices(self) -> dict:
        return self.__high_prices

    @property
    def get_bought(self) -> dict:
        return self.__bought

    @property
    def get_strat_params_list(self) -> dict:
        return self.__strat_params_list
    
    @get_strat_params_list.setter
    def set_strat_params_list(self, strat_params_list: dict) -> None:
        self.__strat_params_list = strat_params_list

    @property
    def get_channel_period(self) -> str:
        return self.get_strat_params_list["channel_period"]
        
    @property
    def get_avg_price_period(self) -> str:
        return self.get_strat_params_list["avg_price_period"]
    
    @property
    def get_signal_name(self) -> dict:
        return self.__signal_name
    
    @property
    def get_events(self) -> Queue:
        return self.__events
    
    @property
    def get_bars(self) -> dExec:
        return self.__bars
    
    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list
    
    def _calculate_initial_bought(self) -> dict:
        bought = {}
        for symbol in self.get_symbol_list:
            bought[symbol] = "OUT"
        return bought

    def _calculate_initial_signal_name(self) -> dict:
        signal_name = {}
        for symbol in self.get_symbol_list:
            signal_name[symbol] = None
        return signal_name

    def _calculate_initial_highLevel(self) -> dict:
        high_level = {}
        for symbol in self.get_symbol_list:
            high_level[symbol] = None
        return high_level
    
    def _calculate_initial_lowlevel(self) -> dict:
        low_level = {}
        for symbol in self.get_symbol_list:
            low_level[symbol] = None
        return low_level

    def calculate_signals(self,
                          event: Event,
                          strat_params_list: dict):
        self.set_strat_params_list = strat_params_list
        event_name = event.get_event_type

        if event_name == "MARKET":
            for symbol in self.get_symbol_list:
                close = self.get_bars.get_latest_bar_value(symbol, "close")
                bar_date = self.get_bars.get_latest_bar_datetime(symbol)
                
                # HighPrices
                bars_high_prices = self.get_bars.get_latest_bars_value(symbol, "high", self.get_avg_price_period + 1)
                if bars_high_prices is not None and bars_high_prices.size >= self.get_avg_price_period + 1:
                    self.get_high_prices[symbol].append(np.mean(bars_high_prices[:self.get_avg_price_period]))

                #LowPrices
                bars_low_prices = self.get_bars.get_latest_bars_value(symbol, "low", self.get_avg_price_period + 1)
                if bars_low_prices is not None and bars_low_prices.size >= self.get_avg_price_period + 1:
                    self.get_low_prices[symbol].append(np.mean(bars_low_prices[:self.get_avg_price_period]))

                #HighLevel
                high_level = None
                if len(self.get_high_prices[symbol]) >= self.get_channel_period:
                    high_level = np.max(self.get_high_prices[symbol][-self.get_channel_period:])
                self.get_high_level[symbol] = high_level

                #LowLevel
                low_level = None
                if len(self.get_low_prices[symbol]) >= self.get_channel_period:
                    low_level = np.min(self.get_low_prices[symbol][-self.get_channel_period:])
                self.get_low_level[symbol] = low_level

                currentBar = convert_str_toDateTime(bar_date)
                expDate = convert_str_toDateTime(instruments_info[symbol]["expiration_date"])

                if high_level and low_level:
                    # LONG
                    if close >= high_level and self.get_bought[symbol] == "OUT" and (expDate - currentBar).days + 1 > 0:
                        self.get_signal_params["signal_name"][symbol] = "LONG"
                        signal = SignalEvent(1, symbol, bar_date, self.get_signal_params)
                        self.get_events.put(signal)
                        self.get_bought[symbol] = self.get_signal_params["signal_name"][symbol]
                        self.get_signal_params["bought"] = self.get_bought
                    #EXIT LONG
                    elif close <= low_level and self.get_bought[symbol] == "LONG":
                        self.get_signal_params["signal_name"][symbol] = "EXIT"
                        signal = SignalEvent(1, symbol, bar_date, self.get_signal_params)
                        self.get_events.put(signal)
                        self.get_bought[symbol] = "OUT"
                    #SHORT
                    elif close <= low_level and self.get_bought[symbol] == "OUT" and (expDate - currentBar).days + 1 > 0:
                        self.get_signal_params["signal_name"][symbol] = "SHORT"
                        signal = SignalEvent(1, symbol, bar_date, self.get_signal_params)
                        self.get_events.put(signal)
                        self.get_bought[symbol] = self.get_signal_params["signal_name"][symbol]
                    #EXIT SHORT
                    elif close >= high_level and self.get_bought[symbol] == "SHORT":
                        self.get_signal_params["signal_name"][symbol] = "EXIT"
                        signal = SignalEvent(1, symbol, bar_date, self.get_signal_params)
                        self.get_events.put(signal)
                        self.get_bought[symbol] = "OUT"
                    #EXIT LONG BY EXPIRATION
                    elif self.get_bought[symbol] == "LONG" and (expDate - currentBar).days + 1 <= 0:
                        self.get_signal_params["signal_name"][symbol] = "EXIT"
                        signal = SignalEvent(1, symbol, bar_date, self.get_signal_params)
                        self.get_events.put(signal)
                        self.get_bought[symbol] = "OUT"
                    #EXIT SHORT BY EXPIRATION
                    elif self.get_bought[symbol] == "SHORT" and (expDate - currentBar).days + 1 <= 0:
                        self.get_signal_params["signal_name"][symbol] = "EXIT"
                        signal = SignalEvent(1, symbol, bar_date, self.get_signal_params)
                        self.get_events.put(signal)
                        self.get_bought[symbol] = "OUT"
                self.get_signal_params["timeindex"] = self.get_bars.get_latest_bar_datetime(symbol)
                self.get_signal_params["signal_name"] = self.get_signal_name
                self.get_signal_params["high_level"] = self.get_high_level
                self.get_signal_params["low_level"] = self.get_low_level

def optimization(*params_list):
    initial_capital = 1_000_000.0
    heartbeat = 0.0
    backtest = Backtest(
        params_list,
        initial_capital,
        heartbeat,
        dExec,
        SimulatedExecutionHandler,
        Portfolio,
        Example_Price_Channel
    )
    backtest.simulate_trading_opt()

if __name__ == "__main__":
    start_time = time.time()
    clear_files()
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
    symbol_list = ["Si-3.20.txt", "Si-6.20.txt"]
    data = dHandl(
        args.folder, 
        data_parser_params, 
        args.timeframe, 
        args.compression,
        symbol_list)
    
    opt_params = {
        "strat_params": {
            "avg_price_period": [6, 8],
            "channel_period": [80, 115]
        },
        "pos_sizer": {
            "pos_sizer_type": ["mpr"],
            "pos_sizer_value": [1, 2]
        },
        "data_iter": data(),
        "args": args
    }
    params_list = optimization_params_handler(opt_params)
    
    with ProcessPoolExecutor(max_workers= 7) as executor:
        results = (executor.map(optimization, params_list))

    end_time = time.time()
    print(f"Elapsed_time= {end_time - start_time}")
