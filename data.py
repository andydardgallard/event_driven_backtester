#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from queue import Queue
import numpy as np
import pandas as pd
from event import MarketEvent
import os
from collections import OrderedDict
from handler import resample_handler

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

    def get_bars_quantity(self, symbol):
        try:
            bars_list = self.__latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return len(bars_list)

class CustomCSVDataHandler():
    def __init__(self, csv_dir, params, timeframe, compression, symbol_list) -> None:
        self.__csv_dir = csv_dir
        self.__params = params
        self.__timeframe = timeframe
        self.__compression = compression
        self.__symbol_list = symbol_list
        self._loader()

        self.__symbol_data = {}
        self._open_convert_csv_files()

    @property
    def get_symbol_data(self) -> dict:
        return self.__symbol_data

    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list

    @property
    def get_csv_dir(self) -> str:
        return self.__csv_dir
    
    @property
    def get_params(self) -> dict:
        return self.__params
    
    @property
    def get_timeframe(self) -> str:
        return self.__timeframe
    
    @property
    def get_compression(self) -> int:
        return self.__compression
    
    def _loader(self) -> None:
        list_of_files = os.listdir(self.get_csv_dir)
        if len(list_of_files) == 0:
            raise ValueError(f"{self.get_csv_dir} is empty!")
        path = self.get_csv_dir

        #parse params
        names = self.get_params.copy()
        {names.pop(key) for key in ["separator", "dtformat", "tmformat", "headers", "timeframe", "timeframebars"]}
        names = {key:value for key, value in names.items() if value >= 0}
        names = dict(sorted(names.items(), key= lambda x:x[1]))

        for file in list_of_files:
            if file in self.get_symbol_list:
                if os.path.isfile(f"{path}/{file}"):
                    #load and parse data
                    with open(f"{path}/{file}", 'r') as fin:
                        dataFrame = pd.read_csv(
                            fin,
                            sep=self.get_params["separator"],
                            header= self.get_params["headers"],
                            names= list(names.keys()),
                            dtype= {"date": str, "time": str},
                            engine= "python"
                            )
                        if self.get_params["time"] != -1:
                            try:
                                dataFrame["datetime"] = pd.to_datetime(dataFrame.pop("date")+' '+dataFrame.pop("time"), format="%Y%m%d %H%M%S")
                                dataFrame = dataFrame.set_index("datetime").sort_index()
                            except:
                                print("The format of headers in dataFile does not match the format of given params!")
                        else:
                            dataFrame = dataFrame.set_index("date").sort_index()
                    
                        #resample data
                        list_of_headers = resample_handler(self.get_params)
                        resampled_df = dataFrame.resample(f'{self.get_compression}{self.get_timeframe}').agg(
                            OrderedDict(list_of_headers)).dropna()
                        self._write_to_csv(resampled_df, file)

    def _write_to_csv(self, dataFrame: pd.DataFrame, file: str, ) -> None:
        if not os.path.exists(f"{self.get_csv_dir}/Temp"):
            os.makedirs(f"{self.get_csv_dir}/Temp")
        dataFrame.to_csv(f"{self.get_csv_dir}/Temp/{file}", mode='w')

    def _open_convert_csv_files(self) -> None:
        comb_index = pd.core.indexes.datetimes.DatetimeIndex
        for symbol in self.get_symbol_list:
            self.__symbol_data[symbol] = pd.read_csv(
                f"{self.__csv_dir}/Temp/{symbol}", 
                header= self.get_params["headers"],
                parse_dates= True,
                ).set_index("datetime").sort_index()
            
            if comb_index.empty:
                comb_index = self.get_symbol_data[symbol].index
            else:
                comb_index = comb_index.union(self.get_symbol_data[symbol].index)

        for symbol in self.get_symbol_list:
            self.__symbol_data[symbol] = self.get_symbol_data[symbol].reindex(
                index= comb_index,
                method= "pad"
            ).to_dict(orient= "index")
            self.__symbol_data[symbol] = iter(self.__symbol_data[symbol].items())
            
        for symbol in self.get_symbol_list:    
            os.remove(f"{self.get_csv_dir}/Temp/{symbol}")
        os.rmdir(f"{self.get_csv_dir}/Temp")

    def __call__(self) -> dict:
        return self.get_symbol_data

class CustomCSVDataExecutor(DataHandler):
    def __init__(self, data_iter: dict, events:Queue) -> None:
        super().__init__()
        self.__data_iter = data_iter
        self.__latest_symbol_data = {key:[] for key in self.__data_iter}
        self.__continue_backtest = True
        self.__events = events

    @property
    def get_continue_backtest(self) -> bool:
        return self.__continue_backtest
    
    @get_continue_backtest.setter
    def set_continue_backtest(self, value: bool) -> None:
        self.__continue_backtest = value

    @property
    def get_latest_symbol_data(self) -> dict:
        return self.__latest_symbol_data

    @property
    def get_data_iter(self) -> dict:
        return self.__data_iter
    
    @property
    def get_symbol_list(self) -> list:
        return list(self.__latest_symbol_data.keys())

    def _get_new_bar(self, symbol: str):
        for data in self.get_data_iter[symbol]:
            yield data

    def get_latest_bar(self, symbol):
        try:
            bars_list = self.get_latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-1]
        
    def get_latest_bars(self, symbol, n=1):
        try:
            bars_list = self.get_latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-n:]
        
    def get_latest_bar_datetime(self, symbol):
        try:
            bars_list = self.get_latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return bars_list[-1][0]
    
    def get_latest_bar_value(self, symbol, value_type):
        try:
            bars_list = self.get_latest_symbol_data[symbol]
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
        for symbol in list(self.__latest_symbol_data.keys()):
            try:
                bar = next(self._get_new_bar(symbol))
            except StopIteration:
                self.set_continue_backtest = False
            else:
                if bar is not None:
                    self.get_latest_symbol_data[symbol].append(bar)       
        self.__events.put(MarketEvent())
    
    def get_bars_quantity(self, symbol):
        try:
            bars_list = self.get_latest_symbol_data[symbol]
        except KeyError:
            print(f"Symbol {symbol} is not in data set!")
            raise
        else:
            return len(bars_list)
    