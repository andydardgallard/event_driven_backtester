#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, queue
import time, portfolio
from data import CustomCSVDataExecutor
from execution import SimulatedExecutionHandler
from pprint import pprint
from handler import convert_str_toDateTime

class Backtest(object):
    '''
    The main handler of events
    '''

    def __init__(
        self,
        params_list: dict,
        data_handler: CustomCSVDataExecutor,
        execution_handler: SimulatedExecutionHandler,
        portfolio: portfolio) -> None:

        self.__data_iter = params_list[1]["data_iter"]
        self.__symbol_list = list(params_list[1]["data_iter"].keys())
        self.__initial_capital = params_list[1]["initial_capital"] * params_list[1]["stratagy_weight"]
        self.__params_list = params_list

        self.__data_handler_cls = data_handler
        self.__execution_handler_cls = execution_handler
        self.__portfolio_cls = portfolio
        self.__stratagy_cls = params_list[1]["stratagy"]

        self.__events = queue.Queue()

        self.__signals = 0
        self.__orders = 0
        self.__fills = 0
        self.__last_bar_dateTime = None

        self.__strat_params_list = params_list[1]["indicators"]
        self.__pos_sizers_params_list = params_list[1]["pos_sizers"]
        self.__margin_params_list = params_list[1]["margin_params"]
        self.__args = params_list[1]["args"]["args"]
        self.start_time = time.time()
        
    @property
    def get_params_list(self) -> dict:
        return self.__params_list[1]
    
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
    def get_margin_params_list(self) -> dict:
        return self.__margin_params_list

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
        self.portfolio = self.__portfolio_cls(self.data_handler, self.get_events, self.get_initial_capital, self.get_params_list, self.stratagy, self.get_stats_mode)
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
                        elif event.get_event_type == "ORDER":
                            self.__orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.get_event_type == "FILL":
                            self.__fills += 1
                            fill_flag = event
        self.__last_bar_dateTime = convert_str_toDateTime(self.data_handler.get_latest_bar_datetime(self.get_symbol_list[0]))

    def _output_performance(self, last_bar_datetime) -> list:
        stats = self.portfolio.output_summary_stats(last_bar_datetime)
        return stats
    
    def _output_portfolio_performance(self, stratagy) -> list:
        stats = self.portfolio.output_portfolio_summary_stats(stratagy)
        return stats

    def simulate_portfolio_trading_visual(self) -> None:
        '''
        Backtest in visiual mode
        '''

        print(f"# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]}", self.get_strat_params_list, self.get_pos_sizers_params_list)
        self._generate_trading_instances()
        self._run_backtest()
        stats, curve = self._output_performance(self.__last_bar_dateTime)
        
        stats_dir = f"{os.getcwd()}/opt_results/visual"
        if not os.path.exists(stats_dir):
            os.makedirs(stats_dir)
        stats_file = f"{stats_dir}/visual_{self.__params_list[1]["stratagy_name"]}.csv"
        with open(stats_file, 'w+') as fout:
            pprint(stats, fout)

        curve_dir = f"{os.getcwd()}/opt_results/visual/temp"
        if not os.path.exists(curve_dir):
            os.makedirs(curve_dir)
        curve_file = f"{curve_dir}/curve_{self.__params_list[1]["stratagy_name"]}.csv"
        with open(curve_file, 'w+') as fout:
            curve.to_csv(curve_file, sep= ';')

        stats_file = f"{curve_dir}/visual_{self.__params_list[1]["stratagy_name"]}.csv"
        with open(stats_file, 'w+') as fout:
            fout.write(str(stats))

    def simulate_portfolio_trading_optimize(self) -> None:
        '''
        Backtest in optimization mode 
        '''
                
        print(f"# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]}", self.get_strat_params_list, self.get_pos_sizers_params_list)
        self._generate_trading_instances()
        self._run_backtest()
        stats, curve = self._output_performance(self.__last_bar_dateTime)
        
        line = {}
        line["stratagy_params"] = self.get_strat_params_list
        line["stratagy_posSizer_params"] = {self.get_pos_sizers_params_list["pos_sizer_type"]: self.get_pos_sizers_params_list["pos_sizer_value"]}
        line["stratagy_stats"] = stats

        result_dir = f"{os.getcwd()}/opt_results/optimize"
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        result_file = f"{result_dir}/{type(self.get_params_list["stratagy_pntr"]).__name__}_{type(self.stratagy).__name__}_{self.get_params_list["args"]["compression"]}{self.get_params_list["args"]["timeframe"]}.csv"
        result = f"# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]}; {line}\n"
        with open(result_file, 'a+') as fout:
            fout.write(result)
        end_time = time.time()
        print(f'# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]} is done! Took {end_time - self.start_time}')
            
        return result
    