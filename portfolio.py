#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from event import FillEvent, OrderEvent, SignalEvent, Event
from performance import calculate_sharp_ratio, get_deal_stats, calculate_winRate, calculate_expected_payoff, calculate_breakeven
from performance import calculate_breakeven_with_tradeoff, calculate_profit_factor, get_holdings_stats, calculate_return, calculate_drawdowns
from performance import calculate_recovery_factor, calculate_sortino_ratio, calculate_apr_to_dd_factor, calculate_var
from data import HistoricCSVDataHandler
from posSizers import mpr
from handler import instruments_info, convert_str_toDateTime
import datetime as dt
import numpy as np
import math
from commission_plans import forts_commission
from risks import marginCall_control
from stratagy import Stratagy

class Portfolio(object):
    '''
    Handler of positions and holdings of backtest. Makes stats.
    '''

    def __init__(self, bars: HistoricCSVDataHandler, events: Event, initial_capital, pos_sizer_params_list, margin_params_list, stratagy: Stratagy, stats_mode: str) -> None:
        self.__bars = bars
        self.__events = events
        self.__symbol_list = self.__bars.get_symbol_list
        self.__initial_capital = initial_capital
        self.__pos_sizer_params_list = pos_sizer_params_list
        self.__margin_params_list = margin_params_list
        self.__stratagy = stratagy
        self.__stats_mode = stats_mode

        self.__all_positions = self.construct_all_positions()
        self.__current_positions = self.construct_current_positions()
        self.__deals_count = 1
        self.__all_holdings = self.construct_all_holdings()
        self.__current_holdings = self.construct_current_holdings()
        self.__equity_curve = None
    
    @property
    def get_stratagy(self) -> Stratagy:
        return self.__stratagy
    
    @property
    def get_stats_mode(self) -> str:
        return self.__stats_mode

    @property
    def get_deals_count(self) -> int:
        return self.__deals_count
    
    @get_deals_count.setter
    def set_deals_count(self, deal_number: int) -> None:
        self.__deals_count = deal_number
    
    @property
    def get_pos_sizer_params_list(self) -> dict:
        return self.__pos_sizer_params_list
    
    @property
    def get_margin_params_list(self) -> dict:
        return self.__margin_params_list

    @property
    def get_bars(self) -> HistoricCSVDataHandler:
        return self.__bars

    @property
    def get_equity_curve(self) -> pd.DataFrame:
        return self.__equity_curve

    @get_equity_curve.setter
    def set_equity_curve(self, curve: pd.DataFrame) -> None:
        self.__equity_curve = curve

    @property
    def get_current_positions(self) -> dict:
        return self.__current_positions

    @property
    def get_current_holdings(self) -> dict:
        return self.__current_holdings

    @property
    def get_all_holdings(self) -> list:
        return self.__all_holdings
    
    @get_all_holdings.setter
    def set_all_holding(self, holds: dict) -> None:
        self.get_all_holdings.append(holds)

    @property
    def get_initial_capital(self) -> float:
        return self.__initial_capital
    
    @property
    def get_symbol_list(self) -> list:
        return self.__symbol_list

    @property
    def get_all_positions(self) -> list:
        return self.__all_positions

    @get_all_positions.setter
    def set_all_positions(self, pos: dict) -> None:
        self.get_all_positions.append(pos)

    def construct_all_positions(self) -> list:
        d = dict((key, value) for key, value in [(symbol, {}) for symbol in self.get_symbol_list])
        d["datetime"] = None
        for symbol in self.get_symbol_list:
            d[symbol]["dealNumber"] = None
            d[symbol]["position"] = 0
            d[symbol]["closedPosition"] = 0
            d[symbol]["entryCapital"] = None
            d[symbol]["entryPrice"] = None
            d[symbol]["entryCommission"] = 0
            d[symbol]["entryDatetime"] = None
            d[symbol]["exitPrice"] = None
            d[symbol]["exitCommission"] = 0
            d[symbol]["exitDatetime"] = None
            d[symbol]["status"] = None
            d[symbol]["dealGrossPnl"] = 0.0
            d[symbol]["commission"] = 0.0
            d[symbol]["dealPnl"] = 0.0
            d[symbol]["signalName"] = None
        return [d]

    def construct_current_positions(self) -> dict:
        d = dict((key, value) for key, value in [(symbol, {}) for symbol in self.get_symbol_list])
        for symbol in self.get_symbol_list:
            d[symbol]["dealNumber"] = None
            d[symbol]["position"] = 0
            d[symbol]["closedPosition"] = 0
            d[symbol]["entryCapital"] = None
            d[symbol]["entryPrice"] = None
            d[symbol]["entryCommission"] = 0
            d[symbol]["entryDatetime"] = None
            d[symbol]["exitPrice"] = None
            d[symbol]["exitCommission"] = 0
            d[symbol]["exitDatetime"] = None
            d[symbol]["status"] = None
            d[symbol]["dealGrossPnl"] = 0.0
            d[symbol]["commission"] = 0.0
            d[symbol]["dealPnl"] = 0.0
            d[symbol]["signalName"] = None
        return d
    
    def construct_all_holdings(self) -> list:
        d = dict((key, value) for key, value in [(symbol, {}) for symbol in self.get_symbol_list])
        d["total"] = {}
        d["total"]["grossPnl"] = 0.0
        d["total"]["pnl"] = 0.0
        d["total"]["cumPnl"] = 0.0
        if self.get_stats_mode == "full":
            d["total"]["longGrossPnl"] = 0.0
            d["total"]["longPnl"] = 0.0
            d["total"]["cumLongPnl"] = 0.0
            d["total"]["shortGrossPnl"] = 0.0
            d["total"]["shortPnl"] = 0.0
            d["total"]["cumShortPnl"] = 0.0
        d["total"]["cash"] = self.get_initial_capital
        d["total"]["blocked"] = 0.0
        d["total"]["capital"] = self.get_initial_capital
        d["datetime"] = None
        
        for symbol in self.get_symbol_list:
            d[symbol]["grossPnl"] = 0.0
            d[symbol]["commission"] = 0.0
            # d[symbol]["marginal_costs"] = 0.0 ##TODO
            d[symbol]["pnl"] = 0.0
            d[symbol]["cumPnl"] = 0.0
            if self.get_stats_mode == "full":
                d[symbol]["longGrossPnl"] = 0.0
                d[symbol]["longCommission"] = 0.0
                d[symbol]["longPnl"] = 0.0
                d[symbol]["cumLongPnl"] = 0.0
                d[symbol]["shortGrossPnl"] = 0.0
                d[symbol]["shortCommission"] = 0.0
                d[symbol]["shortPnl"] = 0.0
                d[symbol]["cumShortPnl"] = 0.0
            d[symbol]["signalName"] = None
        return [d]

    def construct_current_holdings(self) -> dict:
        d = dict((key, value) for key, value in [(symbol, {}) for symbol in self.get_symbol_list])
        d["total"] = {}
        d["total"]["grossPnl"] = 0.0
        d["total"]["pnl"] = 0.0
        d["total"]["cumPnl"] = 0.0
        if self.get_stats_mode == "full":
            d["total"]["longGrossPnl"] = 0.0
            d["total"]["longPnl"] = 0.0
            d["total"]["cumLongPnl"] = 0.0
            d["total"]["shortGrossPnl"] = 0.0
            d["total"]["shortPnl"] = 0.0
            d["total"]["cumShortPnl"] = 0.0
        d["total"]["cash"] = self.get_initial_capital
        d["total"]["blocked"] = 0.0
        d["total"]["capital"] = self.get_initial_capital

        for symbol in self.get_symbol_list:
            d[symbol]["grossPnl"] = 0.0
            d[symbol]["commission"] = 0.0
            # d[symbol]["marginal_costs"] = 0.0
            d[symbol]["pnl"] = 0.0
            d[symbol]["cumPnl"] = 0.0
            if self.get_stats_mode == "full":
                d[symbol]["longGrossPnl"] = 0.0
                d[symbol]["longCommission"] = 0.0
                d[symbol]["longPnl"] = 0.0
                d[symbol]["cumLongPnl"] = 0.0
                d[symbol]["shortGrossPnl"] = 0.0
                d[symbol]["shortCommission"] = 0.0
                d[symbol]["shortPnl"] = 0.0
                d[symbol]["cumShortPnl"] = 0.0
            d[symbol]["signalName"] = None
        return d
    
    def update_timeindex(self, event: Event):
        latest_datetime = self.__bars.get_latest_bar_datetime(self.get_symbol_list[0])

        dp = dict((key, value) for key, value in [(symbol, {}) for symbol in self.get_symbol_list])
        dp["datetime"] = latest_datetime
        for symbol in self.get_symbol_list:
            if self.get_current_positions[symbol]["status"] == "opened":
                self.get_current_positions[symbol]["dealGrossPnl"] = (self.get_bars.get_latest_bar_value(symbol, "close") - self.get_current_positions[symbol]["entryPrice"]) * self.get_current_positions[symbol]["position"]
                self.get_current_positions[symbol]["dealPnl"] = self.get_current_positions[symbol]["dealGrossPnl"] - self.get_current_positions[symbol]["entryCommission"]

            dp[symbol]["dealNumber"] = self.get_current_positions[symbol]["dealNumber"]
            dp[symbol]["position"] = self.get_current_positions[symbol]["position"]
            dp[symbol]["closedPosition"] = self.get_current_positions[symbol]["closedPosition"]
            dp[symbol]["entryCapital"] = self.get_current_positions[symbol]["entryCapital"]
            dp[symbol]["entryPrice"] = self.get_current_positions[symbol]["entryPrice"]
            dp[symbol]["entryCommission"] = self.get_current_positions[symbol]["entryCommission"]
            dp[symbol]["entryDatetime"] = self.get_current_positions[symbol]["entryDatetime"]
            dp[symbol]["exitPrice"] = self.get_current_positions[symbol]["exitPrice"]
            dp[symbol]["exitCommission"] = self.get_current_positions[symbol]["exitCommission"]
            dp[symbol]["exitDatetime"] = self.get_current_positions[symbol]["exitDatetime"]
            dp[symbol]["status"] = self.get_current_positions[symbol]["status"]
            dp[symbol]["dealGrossPnl"] = self.get_current_positions[symbol]["dealGrossPnl"]
            dp[symbol]["dealPnl"] = self.get_current_positions[symbol]["dealPnl"]
            dp[symbol]["signalName"] = self.get_current_positions[symbol]["signalName"]

            self.get_current_positions[symbol]["signalName"] = None
            self.get_current_positions[symbol]["closedPosition"] = 0
            if not self.get_current_positions[symbol]["signalName"] and not self.get_current_positions[symbol]["position"]:
                self.get_current_positions[symbol]["dealNumber"] = None
                self.get_current_positions[symbol]["entryCapital"] = None
                self.get_current_positions[symbol]["entryPrice"] = None
                self.get_current_positions[symbol]["entryCommission"] = 0.0
                self.get_current_positions[symbol]["entryDatetime"] = None
                self.get_current_positions[symbol]["exitPrice"] = None
                self.get_current_positions[symbol]["exitDatetime"] = None
                self.get_current_positions[symbol]["status"] = None
                self.get_current_positions[symbol]["dealGrossPnl"] = 0.0
                self.get_current_positions[symbol]["exitCommission"] = 0.0
                self.get_current_positions[symbol]["dealPnl"] = 0.0
        self.set_all_positions = dp

        dh = dict((key, value) for key, value in [(symbol, {}) for symbol in self.get_symbol_list])
        dh["total"] = {}
        dh["datetime"] = convert_str_toDateTime(latest_datetime)
        for symbol in self.get_symbol_list:
            if len(self.__bars.get_latest_bars_value(symbol, "close", 2)) > 1 and not self.get_current_holdings[symbol]["signalName"]:
                self.get_current_holdings[symbol]["grossPnl"] = self.get_current_positions[symbol]["position"] \
                                                            * (self.__bars.get_latest_bars_value(symbol, "close", 2)[1] \
                                                            - self.__bars.get_latest_bars_value(symbol, "close", 2)[0])
                if np.isnan(self.get_current_holdings[symbol]["grossPnl"]):
                    self.get_current_holdings[symbol]["grossPnl"] = 0.0
                self.get_current_holdings[symbol]["pnl"] = self.get_current_holdings[symbol]["grossPnl"]

                self.get_current_holdings["total"]["grossPnl"] += self.get_current_holdings[symbol]["grossPnl"]
                self.get_current_holdings["total"]["pnl"] += self.get_current_holdings[symbol]["pnl"]
                
                if self.get_current_positions[symbol]["position"] > 0 and self.get_stats_mode == "full":
                    self.get_current_holdings[symbol]["longGrossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
                    self.get_current_holdings[symbol]["longPnl"] = self.get_current_holdings[symbol]["longGrossPnl"]

                    self.get_current_holdings["total"]["longGrossPnl"] += self.get_current_holdings[symbol]["longGrossPnl"]
                    self.get_current_holdings["total"]["longPnl"] += self.get_current_holdings[symbol]["longPnl"]
                elif self.get_current_positions[symbol]["position"] < 0 and self.get_stats_mode == "full":
                    self.get_current_holdings[symbol]["shortGrossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
                    self.get_current_holdings[symbol]["shortPnl"] = self.get_current_holdings[symbol]["shortGrossPnl"]

                    self.get_current_holdings["total"]["shortGrossPnl"] += self.get_current_holdings[symbol]["shortGrossPnl"]
                    self.get_current_holdings["total"]["shortPnl"] += self.get_current_holdings[symbol]["shortPnl"]

            self.get_current_holdings[symbol]["cumPnl"] += self.get_current_holdings[symbol]["pnl"]
            self.get_current_holdings["total"]["cash"] += self.get_current_holdings[symbol]["pnl"]
            self.get_current_holdings["total"]["capital"] += self.get_current_holdings[symbol]["pnl"]
            if self.get_stats_mode == "full":
                self.get_current_holdings[symbol]["cumLongPnl"] += self.get_current_holdings[symbol]["longPnl"]
                self.get_current_holdings[symbol]["cumShortPnl"] += self.get_current_holdings[symbol]["shortPnl"]

            dh[symbol]["grossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
            dh[symbol]["commission"] = self.get_current_holdings[symbol]["commission"]
            dh[symbol]["pnl"] = self.get_current_holdings[symbol]["pnl"]
            dh[symbol]["cumPnl"] = self.get_current_holdings[symbol]["cumPnl"]
            if self.get_stats_mode == "full":
                dh[symbol]["longGrossPnl"] = self.get_current_holdings[symbol]["longGrossPnl"]
                dh[symbol]["longCommission"] = self.get_current_holdings[symbol]["longCommission"]
                dh[symbol]["longPnl"] = self.get_current_holdings[symbol]["longPnl"]
                dh[symbol]["cumLongPnl"] = self.get_current_holdings[symbol]["cumLongPnl"]
                dh[symbol]["shortGrossPnl"] = self.get_current_holdings[symbol]["shortGrossPnl"]
                dh[symbol]["shortCommission"] = self.get_current_holdings[symbol]["shortCommission"]
                dh[symbol]["shortPnl"] = self.get_current_holdings[symbol]["shortPnl"]
                dh[symbol]["cumShortPnl"] = self.get_current_holdings[symbol]["cumShortPnl"]
            dh[symbol]["signalName"] = self.get_current_holdings[symbol]["signalName"]

            self.get_current_holdings[symbol]["signalName"] = None
            self.get_current_holdings[symbol]["commission"] = 0.0
            if self.get_stats_mode == "full":
                self.get_current_holdings[symbol]["longCommission"] = 0.0
                self.get_current_holdings[symbol]["shortCommission"] = 0.0

            if not self.get_current_positions[symbol]["signalName"] and not self.get_current_positions[symbol]["position"]:
                self.get_current_holdings[symbol]["grossPnl"] = 0.0
                if self.get_stats_mode == "full":
                    self.get_current_holdings[symbol]["longGrossPnl"] = 0.0
                    self.get_current_holdings[symbol]["longPnl"] = 0.0
                    self.get_current_holdings[symbol]["shortGrossPnl"] = 0.0
                    self.get_current_holdings[symbol]["shortPnl"] = 0.0
        
        self.get_current_holdings["total"]["cumPnl"] += self.get_current_holdings["total"]["pnl"]
        if self.get_stats_mode == "full":
            self.get_current_holdings["total"]["cumLongPnl"] += self.get_current_holdings["total"]["longPnl"]
            self.get_current_holdings["total"]["cumShortPnl"] += self.get_current_holdings["total"]["shortPnl"]
        
        dh["total"]["grossPnl"] = self.get_current_holdings["total"]["grossPnl"]
        dh["total"]["pnl"] = self.get_current_holdings["total"]["pnl"]
        dh["total"]["cumPnl"] = self.get_current_holdings["total"]["cumPnl"]
        if self.get_stats_mode == "full":
            dh["total"]["longGrossPnl"] = self.get_current_holdings["total"]["longGrossPnl"]
            dh["total"]["longPnl"] = self.get_current_holdings["total"]["longPnl"]
            dh["total"]["cumLongPnl"] = self.get_current_holdings["total"]["cumLongPnl"]
            dh["total"]["shortGrossPnl"] = self.get_current_holdings["total"]["shortGrossPnl"]
            dh["total"]["shortPnl"] = self.get_current_holdings["total"]["shortPnl"]
            dh["total"]["cumShortPnl"] = self.get_current_holdings["total"]["cumShortPnl"]
        dh["total"]["cash"] = self.get_current_holdings["total"]["cash"]
        dh["total"]["blocked"] = abs(self.get_current_holdings["total"]["blocked"])
        dh["total"]["capital"] = self.get_current_holdings["total"]["capital"]

        self.get_current_holdings["total"]["grossPnl"] = 0.0
        self.get_current_holdings["total"]["pnl"] = 0.0
        if self.get_stats_mode == "full":
            self.get_current_holdings["total"]["longGrossPnl"] = 0.0
            self.get_current_holdings["total"]["longPnl"] = 0.0
            self.get_current_holdings["total"]["shortGrossPnl"] = 0.0
            self.get_current_holdings["total"]["shortPnl"] = 0.0

        self.set_all_holding = dh

        if not marginCall_control(dh, dp, self.get_margin_params_list, event):
            for symbol in self.get_symbol_list:
                if self.get_current_positions[symbol]["position"] != 0:
                    self.get_stratagy.get_signal_params["signal_name"][symbol] = "EXIT"
                    marginCall_signal = SignalEvent(1, symbol, latest_datetime, self.get_stratagy.get_signal_params)
                    self.__events.put(marginCall_signal)
                    self.get_stratagy.get_bought[symbol] = "OUT"

    def udate_positions_from_fill(self, fill: FillEvent) -> None:
        symbol = fill.get_symbol
        fill_dir = 0

        if fill.get_direction == "BUY":
            fill_dir = 1
        if fill.get_direction == "SELL":
            fill_dir = -1
        self.get_current_positions[symbol]["position"] += fill_dir * fill.get_quantity
        self.get_current_positions[symbol]["signalName"] = fill.get_signal_params["signal_name"][symbol]

        if fill.get_signal_params["signal_name"][symbol] == "EXIT":
            self.get_current_positions[symbol]["exitPrice"] = self.__bars.get_latest_bar_value(symbol, "open")
            self.get_current_positions[symbol]["exitCommission"] = forts_commission(symbol, self.get_current_positions[symbol]["exitPrice"]) * fill.get_quantity + 1
            self.get_current_positions[symbol]["exitDatetime"] = self.__bars.get_latest_bar_datetime(symbol)
            self.get_current_positions[symbol]["status"] = "closed"
            self.get_current_positions[symbol]["dealGrossPnl"] = (self.get_current_positions[symbol]["exitPrice"] - self.get_current_positions[symbol]["entryPrice"]) * -fill_dir * fill.get_quantity
            self.get_current_positions[symbol]["closedPosition"] = -fill_dir * fill.get_quantity
        else:
            self.get_current_positions[symbol]["dealNumber"] = self.get_deals_count
            self.set_deals_count += 1
            self.get_current_positions[symbol]["entryCapital"] = self.get_current_holdings["total"]["cash"]
            self.get_current_positions[symbol]["entryPrice"] = self.__bars.get_latest_bar_value(symbol, "open")
            self.get_current_positions[symbol]["entryCommission"] = forts_commission(symbol, self.get_current_positions[symbol]["entryPrice"]) * fill.get_quantity - 1
            self.get_current_positions[symbol]["entryDatetime"] = self.__bars.get_latest_bar_datetime(symbol)
            self.get_current_positions[symbol]["exitPrice"] = None
            self.get_current_positions[symbol]["exitCommission"] = 0
            self.get_current_positions[symbol]["exitDatetime"] = None
            self.get_current_positions[symbol]["status"] = "opened"
            self.get_current_positions[symbol]["dealGrossPnl"] = (self.__bars.get_latest_bar_value(symbol, "close") - self.get_current_positions[symbol]["entryPrice"]) * fill_dir * fill.get_quantity
            self.get_current_positions[symbol]["closedPosition"] = 0        
        
        self.get_current_positions[symbol]["dealPnl"] = self.get_current_positions[symbol]["dealGrossPnl"] - self.get_current_positions[symbol]["entryCommission"] - self.get_current_positions[symbol]["exitCommission"] 

    def update_holdings_from_fill(self, fill: FillEvent) -> None:
        symbol = fill.get_symbol
        fill_dir = 0
        if fill.get_direction == "BUY":
            fill_dir = 1
        if fill.get_direction == "SELL":
            fill_dir = -1
            
        self.get_current_holdings[symbol]["signalName"] = fill.get_signal_params["signal_name"][symbol]
        if fill.get_signal_params["signal_name"][symbol] == "EXIT":
            self.get_current_holdings[symbol]["grossPnl"] = -fill_dir * fill.get_quantity \
                                                            * (self.__bars.get_latest_bar_value(symbol, "open") - self.__bars.get_latest_bars_value(symbol, "close", 2)[0])
            self.get_current_holdings[symbol]["commission"] = self.get_current_positions[symbol]["exitCommission"]
            if self.get_stats_mode == "full":
                if fill_dir == -1:
                    self.get_current_holdings[symbol]["longGrossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
                    self.get_current_holdings[symbol]["longCommission"] = self.get_current_holdings[symbol]["commission"]
                    self.get_current_holdings[symbol]["longPnl"] = self.get_current_holdings[symbol]["longGrossPnl"] - self.get_current_holdings[symbol]["commission"]
                else:
                    self.get_current_holdings[symbol]["shortGrossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
                    self.get_current_holdings[symbol]["shortCommission"] = self.get_current_holdings[symbol]["commission"]
                    self.get_current_holdings[symbol]["shortPnl"] = self.get_current_holdings[symbol]["shortGrossPnl"] - self.get_current_holdings[symbol]["commission"]
            if instruments_info[symbol]["type"] == "futures":
                self.get_current_holdings["total"]["cash"] += instruments_info[symbol]["margin"] * fill.get_quantity
                self.get_current_holdings["total"]["blocked"] += instruments_info[symbol]["margin"] * fill.get_quantity
        else:
            self.get_current_holdings[symbol]["grossPnl"] = -fill_dir * fill.get_quantity \
                                                        * (self.__bars.get_latest_bar_value(symbol, "open") - self.__bars.get_latest_bar_value(symbol, "close"))
            self.get_current_holdings[symbol]["commission"] = self.get_current_positions[symbol]["entryCommission"]
            if self.get_stats_mode == "full":
                if fill_dir == 1:
                    self.get_current_holdings[symbol]["longGrossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
                    self.get_current_holdings[symbol]["longCommission"] = self.get_current_holdings[symbol]["commission"]
                    self.get_current_holdings[symbol]["longPnl"] = self.get_current_holdings[symbol]["longGrossPnl"] - self.get_current_holdings[symbol]["commission"]
                else:
                    self.get_current_holdings[symbol]["shortGrossPnl"] = self.get_current_holdings[symbol]["grossPnl"]
                    self.get_current_holdings[symbol]["shortCommission"] = self.get_current_holdings[symbol]["commission"]
                    self.get_current_holdings[symbol]["shortPnl"] = self.get_current_holdings[symbol]["shortGrossPnl"] - self.get_current_holdings[symbol]["commission"]
            if instruments_info[symbol]["type"] == "futures":
                self.get_current_holdings["total"]["cash"] -= instruments_info[symbol]["margin"] * fill.get_quantity
                self.get_current_holdings["total"]["blocked"] -= instruments_info[symbol]["margin"] * fill.get_quantity
        self.get_current_holdings[symbol]["pnl"] = self.get_current_holdings[symbol]["grossPnl"] - self.get_current_holdings[symbol]["commission"]
        
        self.get_current_holdings["total"]["grossPnl"] += self.get_current_holdings[symbol]["grossPnl"]
        self.get_current_holdings["total"]["pnl"] += self.get_current_holdings[symbol]["pnl"]
        if self.get_stats_mode == "full":
            self.get_current_holdings["total"]["longGrossPnl"] += self.get_current_holdings[symbol]["longGrossPnl"]
            self.get_current_holdings["total"]["longPnl"] += self.get_current_holdings[symbol]["longPnl"]
            self.get_current_holdings["total"]["shortGrossPnl"] += self.get_current_holdings[symbol]["shortGrossPnl"]
            self.get_current_holdings["total"]["shortPnl"] += self.get_current_holdings[symbol]["shortPnl"]

    def update_fill(self, event: FillEvent) -> None:
        if event.get_event_type == "FILL":
            self.udate_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal: SignalEvent) -> OrderEvent:
        order = None
        symbol = signal.get_symbol
        signal_name = signal.get_signal_params["signal_name"][symbol]
        timeindx = signal.get_datetime
        cur_quantity = self.get_current_positions[symbol]["position"]
        order_type = "MKT"
        pos_sizer_type = self.get_pos_sizer_params_list["pos_sizer_type"]
        cash = self.get_current_holdings["total"]["cash"]
        mpr_ = self.get_pos_sizer_params_list["pos_sizer_value"]

        if signal_name == "LONG" and cur_quantity == 0 and cash > 0:
            if pos_sizer_type == "mpr":
                entry_price = self.get_bars.get_latest_bar_value(symbol, "high")
                exit_price = signal.get_signal_params["low_level"][symbol]
                mkt_quantity = min(mpr(symbol, cash, mpr_, exit_price, entry_price), math.floor(cash / instruments_info[symbol]["margin"]))
                mkt_quantity = 1 if mkt_quantity == 0 else mkt_quantity
            else:
                entry_price = self.get_bars.get_latest_bar_value(symbol, "high")
                mkt_quantity = 1
            if marginCall_control(self.get_current_holdings, mkt_quantity, self.get_margin_params_list, signal):
                order = OrderEvent(symbol, order_type, mkt_quantity, "BUY", signal.get_signal_params, timeindx)
        
        if signal_name == "SHORT" and cur_quantity == 0 and cash > 0:
            if pos_sizer_type == "mpr":
                entry_price = self.get_bars.get_latest_bar_value(symbol, "low")
                exit_price = signal.get_signal_params["high_level"][symbol]
                mkt_quantity = min(mpr(symbol, cash, mpr_, exit_price, entry_price), math.floor(cash / instruments_info[symbol]["margin"]))
                mkt_quantity = 1 if mkt_quantity == 0 else mkt_quantity
            else:
                entry_price = self.get_bars.get_latest_bar_value(symbol, "low")
                mkt_quantity = 1
            if marginCall_control(self.get_current_holdings, mkt_quantity, self.get_margin_params_list, signal):
                order = OrderEvent(symbol, order_type, mkt_quantity, "SELL", signal.get_signal_params, timeindx)

        if signal_name == "EXIT" and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), "SELL", signal.get_signal_params, timeindx)
        if signal_name == "EXIT" and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), "BUY", signal.get_signal_params, timeindx)
        return order

    #TODO def market_order
    #TODO def limit_order
    #TODO def margin_call

    def update_signal(self, event: Event) -> None:
        if event.get_event_type == "SIGNAL":
            order_event = self.generate_naive_order(event)
            self.__events.put(order_event)
    
    def output_summary_stats(self, last_bar_datetime) -> list:
        deals_stats = get_deal_stats(self.get_all_positions, self.get_symbol_list, self.get_initial_capital, self.get_stats_mode)
        deals_stats = calculate_winRate(deals_stats, self.get_symbol_list, self.get_stats_mode)
        deals_stats = calculate_expected_payoff(deals_stats, self.get_symbol_list, self.get_stats_mode)
        deals_stats = calculate_breakeven(deals_stats, self.get_symbol_list, self.get_stats_mode)
        deals_stats = calculate_breakeven_with_tradeoff(deals_stats, self.get_symbol_list, 0.1, self.get_stats_mode)
        deals_stats = calculate_profit_factor(deals_stats, self.get_symbol_list, self.get_stats_mode)
        holdings_stats = get_holdings_stats(deals_stats, self.get_all_holdings, self.get_symbol_list, last_bar_datetime, self.get_stats_mode)
        holdings_stats = calculate_return(holdings_stats)
        holdings_stats = calculate_drawdowns(holdings_stats, self.get_all_holdings)
        holdings_stats = calculate_apr_to_dd_factor(holdings_stats)
        holdings_stats = calculate_recovery_factor(holdings_stats)
        holdings_stats = calculate_sharp_ratio(holdings_stats, self.get_all_holdings)
        holdings_stats = calculate_sortino_ratio(holdings_stats, self.get_all_holdings)
        holdings_stats = calculate_var(holdings_stats, self.get_all_holdings, 6500, 0.01, 10)
        return holdings_stats
