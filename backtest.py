#!/usr/bin/python
# -*- coding: utf-8 -*-

import pprint, time, portfolio, stratagy
import queue
from data import HistoricCSVDataHandler
from execution import SimulatedExecutionHandler
from pprint import pprint

class Backtest(object):
    def __init__(
        self,
        csv_dir: str,
        symbol_list: list,
        initial_capital: float,
        heartbeat,
        start_date,
        data_handler: HistoricCSVDataHandler,
        execution_handler: SimulatedExecutionHandler,
        portfolio: portfolio,
        stratagy: stratagy,
        strat_params_list: dict) -> None:
        
        self.__csv_dir = csv_dir
        self.__symbol_list = symbol_list
        self.__initial_capital = initial_capital
        self.__heartbeat = heartbeat
        self.__start_date = start_date

        self.__data_handler_cls = data_handler
        self.__execution_handler_cls = execution_handler
        self.__portfolio_cls = portfolio
        self.__stratagy_cls = stratagy

        self.__events = queue.Queue()

        self.__signals = 0
        self.__orders = 0
        self.__fills = 0
        self.__num_stats = 1

        self.__strat_params_list = strat_params_list

    @property
    def get_strat_params_list(self) -> dict:
        return self.__strat_params_list

    @property
    def get_initial_capital(self) -> float:
        return self.__initial_capital

    @property
    def get_start_date(self) -> None:
        return self.__start_date
    
    @property
    def get_events(self) -> queue.Queue:
        return self.__events

    @property
    def get_csv_dir(self) -> str:
        return self.__csv_dir

    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list

    def _generate_trading_instances(self) -> None:
        print("Creating Data Handler, Stratagy, Portfolio and ExecutionHandler")
        self.data_handler =  self.__data_handler_cls(self.get_events, self.get_csv_dir, self.get_symbol_list)
        self.stratagy = self.__stratagy_cls(self.data_handler, self.get_events)
        self.portfolio = self.__portfolio_cls(self.data_handler, self.get_events, self.get_start_date, self.get_initial_capital)
        self.execution_handler = self.__execution_handler_cls(self.get_events)

    def _run_backtest(self) -> None:
        i = 0
        fill_flag = None
        while True:
            i += 1
            if self.data_handler.get_continue_backtest == True:
                self.data_handler.update_bars()
            else:
                break

            while True:
                try:
                    event = self.get_events.get(block=False)
                except queue.Empty:
                    break
                else:
                    if event is not None:
                        if event.get_event_type == "MARKET":
                            self.stratagy.calculate_signals(event, self.get_strat_params_list[0][0], self.get_strat_params_list[0][1])
                            self.portfolio.update_timeindex()
                            if fill_flag:
                                self.portfolio.update_fill(fill_flag)
                                fill_flag = None
                        elif event.get_event_type == "SIGNAL":
                            self.__signals += 1
                            self.portfolio.update_signal(event)
                        elif event.get_event_type == "ORDER":
                            self.__orders += 1
                            self.execution_handler.execute_order(event)
                        elif event.get_event_type == "FILL":
                            self.__fills += 1
                            fill_flag = event
            time.sleep(self.__heartbeat)

    def _output_performance(self) -> list:
        self.portfolio.create_equity_curve_dataframe()
        print("Create summary stats ...")
        stats = self.portfolio.output_summary_stats()
        print("Creating equity curve ...")
        # print(self.portfolio.get_equity_curve.tail(10))
        # pprint(stats)
        return stats

    def simulate_trading_visio(self) -> None:
        # self._generate_trading_instances(sp)
        self._run_backtest()
        stats = self._output_performance()
        pprint(stats)

    # def simulate_functions(self, sp) -> None:
    #     self._generate_trading_instances(sp)
    #     self._run_backtest(sp)
    #     stats = self._output_performance()
    #     pprint(stats)

    def simulate_trading_opt(self, params_list) -> None:
        print(f"Params= {self.get_strat_params_list[0][0]} - {self.get_strat_params_list[0][1]}")
        self._generate_trading_instances()
        self._run_backtest()
        stats = self._output_performance()
        pprint(stats)

        with open("opt.csv", 'a') as fout:
            total_return = float(stats[0][1].replace("%", ""))
            sharp = float(stats[1][1])
            max_dd = float(stats[2][1].replace("%", ""))
            dd_dur = int(stats[3][1])
            fout.write(f"{self.get_strat_params_list[0][0]}, {self.get_strat_params_list[0][1]}, {total_return}, {sharp}, {max_dd}, {dd_dur}\n")
            
