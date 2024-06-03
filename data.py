#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from queue import Queue
import numpy as np
import pandas as pd
from event import MarketEvent

class DataHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get_latest_bar(self, symbol):
        raise NotImplementedError("Should implement get_latest_bar()")
    
    @abstractmethod
    def get_latest_bars(self, symbol, n=1):
        raise NotImplementedError("Should implement get_latest_bars()")

    @abstractmethod
    def get_latest_bar_datetime(self, symbol):
        raise NotImplementedError("Should implement get_latest_bar_datetime()")

    @abstractmethod
    def get_latest_bar_value(self, symbol, value_type):
        raise NotImplementedError("Should implement get_latest_bar_value()")

    @abstractmethod
    def get_latest_bars_value(self, symbol, value_type, n=1):
        raise NotImplementedError("Should implement get_latest_bars_value()")

    @abstractmethod
    def update_bars(self):
        raise NotImplementedError("Should implement update_bars()")

    @abstractmethod
    def get_bars_quantity(self, symbol):
        raise NotImplementedError("Should implement get_bars_quantity()")

class HistoricCSVDataHandler(DataHandler):
    def __init__(self, events: Queue, csv_dir: str, symbol_list: list) -> None:
        self.__events = events
        self.__csv_dir = csv_dir
        self.__symbol_list = symbol_list

        self.__symbol_data = {}
        self.__latest_symbol_data = {}
        self.__continue_backtest = True

        self._open_convert_csv_files()

    @property
    def get_latest_symbol_data(self) -> dict:
        return self.__latest_symbol_data

    @property
    def get_symbol_data(self) -> dict:
        return self.__symbol_data

    @property
    def get_continue_backtest(self) -> bool:
        return self.__continue_backtest

    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list

    @property
    def get_event(self) -> Queue:
        return self.__events

    def _open_convert_csv_files(self):
        comb_index = pd.core.indexes.datetimes.DatetimeIndex
        for symbol in self.__symbol_list:
            self.__symbol_data[symbol] = pd.read_csv(
                f"{self.__csv_dir}/{symbol}", 
                header= 0,
                parse_dates= True,
                names= ["date", "time", "open", "high", "low", "close", "vol"]
                )
            a = self.__symbol_data[symbol].pop("time").to_numpy()
            a, s = np.divmod(a, 100)
            h, m = np.divmod(a, 100)
            self.__symbol_data[symbol]["datetime"] = (
                pd.to_datetime(self.__symbol_data[symbol].pop("date"), format= "%Y%m%d")
                + pd.to_timedelta(h*3600+m*60+s, unit='s'))
            self.__symbol_data[symbol] = self.__symbol_data[symbol].set_index("datetime").sort_index()

            if comb_index.empty:
                comb_index = self.__symbol_data[symbol].index
            else:
                comb_index = comb_index.union(self.__symbol_data[symbol].index)
            self.__latest_symbol_data[symbol] = []

        for symbol in self.__symbol_list:
            self.__symbol_data[symbol] = self.__symbol_data[symbol].reindex(
                index= comb_index,
                method= "pad"
            ).to_dict(orient= "index")#.iterrows()
            self.__symbol_data[symbol] = iter(self.__symbol_data[symbol].items())

    def _get_new_bar(self, symbol):
        for data in self.__symbol_data[symbol]:
            yield data
    
    def get_latest_bar(self, symbol):
        try:
            bars_list = self.__latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-1]

    def get_latest_bars(self, symbol, n=1):
        try:
            bars_list = self.__latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-n:]

    def get_latest_bar_datetime(self, symbol):
        try:
            bars_list = self.__latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-1][0]

    def get_latest_bar_value(self, symbol, value_type):
        try:
            bars_list = self.__latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-1][1][value_type]
    
    def get_latest_bars_value(self, symbol, value_type, n=1):
        try:
            bars_list = self.get_latest_bars(symbol, n)
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return np.array([data[1][value_type] for data in bars_list])

    def update_bars(self):
        for symbol in self.__symbol_list:
            try:
                bar = next(self._get_new_bar(symbol))
            except StopIteration:
                self.__continue_backtest = False
            else:
                if bar is not None:
                    self.__latest_symbol_data[symbol].append(bar)
        self.__events.put(MarketEvent())
        # self.__events.put(MarketEvent())

    def get_bars_quantity(self, symbol):
        try:
            bars_list = self.__latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return len(bars_list)
            