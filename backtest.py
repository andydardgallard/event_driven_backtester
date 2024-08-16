#!/usr/bin/python
# -*- coding: utf-8 -*-

import time, portfolio, stratagy
import queue
from data import CustomCSVDataExecutor
from execution import SimulatedExecutionHandler
from handler import convert_str_toDateTime
from pprint import pprint

class Backtest(object):
    def __init__(
        self,
        params_list: dict,
        initial_capital: float,
        heartbeat,
        data_handler: CustomCSVDataExecutor,
        execution_handler: SimulatedExecutionHandler,
        portfolio: portfolio,
        stratagy: stratagy) -> None:

        self.__data_iter = params_list[0]["data_iter"]
        self.__symbol_list = list(params_list[0]["data_iter"].keys())
        self.__initial_capital = initial_capital
        self.__heartbeat = heartbeat

        self.__data_handler_cls = data_handler
        self.__execution_handler_cls = execution_handler
        self.__portfolio_cls = portfolio
        self.__stratagy_cls = stratagy

        self.__events = queue.Queue()

        self.__signals = 0
        self.__orders = 0
        self.__fills = 0
        self.__last_bar_dateTime = None

        self.__strat_params_list = params_list[0]["indicators"]
        self.__pos_sizers_params_list = params_list[0]["pos_sizers"]
        self.__args = params_list[0]["args"]
        
    @property
    def get_args(self):
        return self.__args

    @property
    def get_stats_mode(self) -> str:
        return self.__args.stats_mode
    
    @property
    def get_pos_sizers_params_list(self) -> dict:
        return self.__pos_sizers_params_list

    @property
    def get_strat_params_list(self) -> dict:
        return self.__strat_params_list

    @property
    def get_initial_capital(self) -> float:
        return self.__initial_capital
    
    @property
    def get_events(self) -> queue.Queue:
        return self.__events

    @property
    def get_data_iter(self) -> str:
        return self.__data_iter

    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list

    def _generate_trading_instances(self) -> None:
        self.data_handler = self.__data_handler_cls(self.get_data_iter, self.get_events)
        self.stratagy = self.__stratagy_cls(self.data_handler, self.get_events)
        self.portfolio = self.__portfolio_cls(self.data_handler, self.get_events, self.get_initial_capital, self.get_pos_sizers_params_list, self.get_stats_mode)
        self.execution_handler = self.__execution_handler_cls(self.get_events)

    def _run_backtest(self) -> None:
        i = 0
        fill_flag = None
        while self.data_handler.get_continue_backtest:
            i += 1
            if self.data_handler.get_continue_backtest == True:
                self.data_handler.update_bars()
            
            while self.data_handler.get_continue_backtest:
                try:
                    event = self.get_events.get(block=False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.get_event_type == "MARKET":
                            if fill_flag:
                                self.portfolio.update_fill(fill_flag)
                                fill_flag = 0
                            self.stratagy.calculate_signals(event, self.get_strat_params_list)
                            self.portfolio.update_timeindex(event)
                            if self.portfolio.get_current_holdings["total"]["capital"] < 0:
                                self.data_handler.set_continue_backtest = False
                        elif event.get_event_type == "SIGNAL":
                            self.__signals += 1
                            self.portfolio.update_signal(event)
                        elif event.get_event_type == "MARGINCALL":
                            self.execution_handler.execute_margin_call(event) #TODO marginCall_executor
                            self.data_handler.set_continue_backtest = False
                        elif event.get_event_type == "ORDER":
                            self.__orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.get_event_type == "FILL":
                            self.__fills += 1
                            fill_flag = event
            time.sleep(self.__heartbeat)
        self.__last_bar_dateTime = convert_str_toDateTime(self.data_handler.get_latest_bar_datetime(self.get_symbol_list[0]))

    def _output_performance(self, last_bar_datetime) -> list:
        stats = self.portfolio.output_summary_stats(last_bar_datetime)
        return stats

    def simulate_trading_opt(self) -> None:
        print(self.get_strat_params_list, self.get_pos_sizers_params_list)
        self._generate_trading_instances()
        self._run_backtest()

        stats = self._output_performance(self.__last_bar_dateTime)
        pprint(stats)
        line = {}
        line["stratagy_params"] = self.get_strat_params_list
        line["stratagy_posSizer_params"] = self.get_pos_sizers_params_list
        line["stratagy_stats"] = stats

        with open(f"opt_{type(self.stratagy).__name__}_{self.get_args.compression}{self.get_args.timeframe}_{self.get_symbol_list}.csv", 'a') as fout:
            fout.write(f"{line}\n")
