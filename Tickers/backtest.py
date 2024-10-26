#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import time, portfolio
import queue
from data import CustomCSVDataExecutor
from execution import SimulatedExecutionHandler
from pprint import pprint
from handler import convert_str_toDateTime
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

class Backtest(object):
    def __init__(
        self,
        params_list: dict,
        data_handler: CustomCSVDataExecutor,
        execution_handler: SimulatedExecutionHandler,
        portfolio: portfolio) -> None:

        self.__data_iter = params_list[1]["data_iter"]
        self.__symbol_list = list(params_list[1]["data_iter"].keys())
        self.__initial_capital = params_list[1]["initial_capital"]
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
        self.__args = params_list[1]["args"]
        self.start_time = time.time()
        
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
        self.portfolio = self.__portfolio_cls(self.data_handler, self.get_events, self.get_initial_capital, self.get_pos_sizers_params_list, self.get_margin_params_list, self.stratagy, self.get_stats_mode)
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
                                # print(f"{i}, FILL, {fill_flag.get_symbol}, {self.data_handler.get_latest_bar(fill_flag.get_symbol)}, CP={self.portfolio.get_current_positions}, {fill_flag.get_signal_params}")
                                fill_flag = 0
                            self.stratagy.calculate_signals(event, self.get_strat_params_list)
                            self.portfolio.update_timeindex(event)
                            if self.portfolio.get_current_holdings["total"]["capital"] < 0:
                                self.data_handler.set_continue_backtest = False
                            # for symbol in self.get_symbol_list:
                            #     print(f"{i}, MARKET, {symbol}, {self.data_handler.get_latest_bar(symbol)}, {self.stratagy.get_signal_params}, {self.portfolio.get_current_positions}")
                        elif event.get_event_type == "SIGNAL":
                            self.__signals += 1
                            self.portfolio.update_signal(event)
                            # print(f"{i}, SIGNAL, {event.get_symbol}, {self.data_handler.get_latest_bar(event.get_symbol)}, {event.get_signal_params}")
                        # elif event.get_event_type == "MARGINCALL":
                        # #     self.execution_handler.execute_margin_call(event) #TODO marginCall_executor
                        #     # self.data_handler.set_continue_backtest = False
                        #     print(f"{i}, MARGINCALL, {event.get_symbol}, {self.portfolio.get_current_positions}")
                        elif event.get_event_type == "ORDER":
                            self.__orders += 1
                            self.execution_handler.execute_order(event)
#                             print(f"{i}, ORDER, {event.get_symbol}, {self.data_handler.get_latest_bar(event.get_symbol)}, quantity= {event.get_quantity}, \
# direction= {event.get_direction}, timeindx= {event.get_timeindx}, {event.get_signal_params}")
                        elif event.get_event_type == "FILL":
                            # self.portfolio.update_fill(event)
                            self.__fills += 1
                            fill_flag = event
            # time.sleep(self.__heartbeat)
        self.__last_bar_dateTime = convert_str_toDateTime(self.data_handler.get_latest_bar_datetime(self.get_symbol_list[0]))

    def _output_performance(self, last_bar_datetime) -> list:
        stats = self.portfolio.output_summary_stats(last_bar_datetime)
        return stats

    def plot_results_abs(self) -> None:
        x = [x["datetime"] for x in self.portfolio.get_all_holdings]
        y1 = [y["total"]["cumPnl"] for y in self.portfolio.get_all_holdings]
        capital = [i["total"]["capital"] for i in self.portfolio.get_all_holdings]

        hwm = [0]
        drawdown_pct = [0]
        drawdown_pcr = [0]
        for i in range(len(capital)):
            hwm.append(0)
            hwm[i] = (max(hwm[i - 1], capital[i]))

            drawdown_pct.append(0)
            drawdown_pct[i] = (hwm[i] - capital[i]) * -1

            drawdown_pcr.append(0)
            drawdown_pcr[i] = (drawdown_pct[i] / hwm[i]) * 100

        del drawdown_pct[i + 1]
        del drawdown_pcr[i + 1]

        returns = pd.Series(capital).pct_change().fillna(0)
        returns = returns.apply(lambda x: x * 100).cumsum()

        y1 = np.array(y1)
        fig, ax = plt.subplots(2, 2, figsize=(14, 8))
        fig.canvas.manager.set_window_title("Cumulative PnL vs Drawdown_pct") 

        color = 'tab:blue'
        ax[0, 0].plot(x, y1, color)
        ax[0, 0].set_ylabel('PnL', color=color)
        ax[0, 0].tick_params(axis='y', labelcolor=color)
        ax[0, 0].grid(True)
        ax[0, 0].fill_between(x, y1, 0, where= (y1>=0), interpolate=True, color= color)
        ax[0, 0].fill_between(x, y1, 0, where= (y1<0), interpolate=True, color='red')
        ax[0, 0].set_xticklabels([])

        ax[0, 1].plot(x, returns, color)
        ax[0, 1].set_ylabel('Returns, %', color= color, rotation= -90, labelpad= 15)
        ax[0, 1].yaxis.set_label_position("right")
        ax[0, 1].yaxis.tick_right()
        ax[0, 1].tick_params(axis='y', labelcolor=color)
        ax[0, 1].grid(True)
        ax[0, 1].fill_between(x, returns, 0, where= (y1>=0), interpolate=True, color= color)
        ax[0, 1].fill_between(x, returns, 0, where= (y1<0), interpolate=True, color='red')
        ax[0, 1].set_xticklabels([])

        color = "tab:red"
        ax[1, 0].plot(x, drawdown_pct, color)
        ax[1, 0].set_xlabel('dates')
        ax[1, 0].set_ylabel('Drawdown_pct', color=color)
        ax[1, 0].tick_params(axis='y', labelcolor=color)
        ax[1, 0].fill_between(x, drawdown_pct, color= color)
        ax[1, 0].grid(True)

        ax[1, 1].plot(x,drawdown_pcr, color)
        ax[1, 1].set_xlabel('dates')
        ax[1, 1].set_ylabel('Drawdown_prc, %', color= color, rotation= -90, labelpad= 15)
        ax[1, 1].yaxis.set_label_position("right")
        ax[1, 1].yaxis.tick_right()
        ax[1, 1].tick_params(axis= 'y', labelcolor= color)
        ax[1, 1].fill_between(x, drawdown_pcr, color= color)
        ax[1, 1].grid(True)
        plt.subplots_adjust(hspace=0, wspace=0)
        plt.show()

    def simulate_trading_visual(self) -> None:
        print(f"# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]}", self.get_strat_params_list, self.get_pos_sizers_params_list)
        self._generate_trading_instances()
        self._run_backtest()
        stats = self._output_performance(self.__last_bar_dateTime)
        with open("visual.csv", 'w+') as fout:
            pprint(stats, fout)
        self.plot_results_abs()

    def simulate_trading_opt(self) -> None:
        print(f"# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]}", self.get_strat_params_list, self.get_pos_sizers_params_list)
        self._generate_trading_instances()
        self._run_backtest()
        stats = self._output_performance(self.__last_bar_dateTime)
        # pprint(stats)
        line = {}
        line["stratagy_params"] = self.get_strat_params_list
        line["stratagy_posSizer_params"] = {self.get_pos_sizers_params_list["pos_sizer_type"]: self.get_pos_sizers_params_list["pos_sizer_value"]}
        line["stratagy_stats"] = stats

        result_dir = f"{os.getcwd()}/opt_results"
        if not os.path.exists(result_dir):
            os.makedirs(result_dir)
        # strat_params = "_".join((str(v) for v in self.get_strat_params_list.values()))
        result_file = f"{result_dir}/{type(self.stratagy).__name__}_{self.get_args.compression}{self.get_args.timeframe}.csv"
        result = f"# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]}; {line}\n"
        with open(result_file, 'a+') as fout:
            fout.write(result)
        end_time = time.time()
        print(f'# {self.__params_list[1]["item_number"]} from {self.__params_list[1]["length"]} is done! Took {end_time - self.start_time}')



        # for i in self.portfolio.get_all_holdings:
        #     print(i)

        # for i in self.portfolio.get_all_positions:
        #     print(i)
        return result
            