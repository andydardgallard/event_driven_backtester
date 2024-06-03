#!/usr/bin/python
# -*- coding: utf-8 -*-

import pandas as pd
from event import FillEvent, OrderEvent, SignalEvent, Event
from performance import create_sharp_ratio, create_drawdowns
from data import HistoricCSVDataHandler

class Portfolio(object):
    def __init__(self, bars: HistoricCSVDataHandler, events: Event, start_date, initial_capital = 1_000_000) -> None:
        self.__bars = bars
        self.__events = events
        self.__symbol_list = self.__bars.get_symbol_list
        self.__start_date = start_date
        self.__initial_capital = initial_capital

        self.__all_positions = self.construct_all_positions()
        self.__current_positions = self.construct_current_positions()
        self.__all_holdings = self.construct_all_holdings()
        self.__current_holdings = self.construct_current_holdings()

        self.__equity_curve = None
    
    # @

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
    
    @get_current_positions.setter
    def set_current_positions(self, pos: dict) -> None:
        self.__current_positions = pos

    @property
    def get_current_holdings(self) -> dict:
        return self.__current_holdings

    # @get_current_holdings.setter
    # def set_current_holdings(self, fill: FillEvent, cost: float) -> None:
    #     self.get_current_holdings[fill.get_symbol] += cost
    #     self.get_current_holdings["commission"] += fill.get_commission
    #     self.get_current_holdings["cash"] -= (cost + fill.get_commission)
    #     self.get_current_holdings["total"] -= (cost + fill.get_commission)

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
    def get_start_date(self) -> None:
        return  self.__start_date

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
        d = dict((key, value) for key, value in [(symbol, 0) for symbol in self.get_symbol_list])
        d["datetime"] = self.get_start_date
        d["price"] = 0.0
        return [d]

    def construct_all_holdings(self) -> list:
        d = dict((key, value) for key, value in [(symbol, 0.0) for symbol in self.get_symbol_list])
        d["datetime"] = self.get_start_date
        d["cash"] = self.get_initial_capital
        d["commission"] = 0.0
        d["total"] = self.get_initial_capital
        # d["price"] = 0.0
        return [d]

    def construct_current_holdings(self) -> dict:
        d = dict((key, value) for key, value in [(symbol, 0.0) for symbol in self.get_symbol_list])
        d["cash"] = self.get_initial_capital
        d["commission"] = 0.0
        d["total"] = self.get_initial_capital
        # d["price"] = 0.0
        return d
    
    def construct_current_positions(self) -> dict:
        d = dict((key, value) for key, value in [(symbol, 0) for symbol in self.get_symbol_list])
        d["price"] = 0.0
        return d
    
    def update_timeindex(self):
        latest_datetime = self.__bars.get_latest_bar_datetime(self.get_symbol_list[0])

        dp = dict((key, value) for key, value in [(symbol, 0) for symbol in self.get_symbol_list])
        dp["datetime"] = latest_datetime
        for symbol in self.get_symbol_list:
            dp[symbol] = self.get_current_positions[symbol]
            dp["price"] = 0.0
        self.set_all_positions = dp

        dh = dict((key, value) for key, value in [(symbol, 0.0) for symbol in self.get_symbol_list])
        dh["datetime"] = latest_datetime
        dh["cash"] = self.get_current_holdings["cash"]
        dh["commission"] = self.get_current_holdings["commission"]
        dh["total"] = self.get_current_holdings["total"]
        for symbol in self.get_symbol_list:
            market_value = self.get_current_positions[symbol] * self.__bars.get_latest_bar_value(symbol, "close")
            dh[symbol] = market_value
            dh["total"] == market_value
            # dh["price"] = self.__bars.get_latest_bar_value(symbol, "close")
        self.set_all_holding = dh

    def udate_positions_from_fill(self, fill: FillEvent) -> None:
        fill_dir = 0
        if fill.get_direction == "BUY":
            fill_dir = 1
        if fill.get_direction == "SELL":
            fill_dir = -1
        self.set_current_positions[fill.get_symbol] += fill_dir * fill.get_quantity
        self.get_current_positions["price"] = self.__bars.get_latest_bar_value(fill.get_symbol, "open")

    def update_holdings_from_fill(self, fill: FillEvent) -> None:
        fill_dir = 0
        if fill.get_direction == "BUY":
            fill_dir = 1
        if fill.get_direction == "SELL":
            fill_dir = -1
        fill_cost = self.__bars.get_latest_bar_value(fill.get_symbol, "open")
        cost = fill_dir * fill.get_quantity * fill_cost
        self.get_current_holdings[fill.get_symbol] += cost
        self.get_current_holdings["commission"] += fill.get_commission
        self.get_current_holdings["cash"] -= (cost + fill.get_commission)
        self.get_current_holdings["total"] -= (cost + fill.get_commission)
        # self.get_current_holdings["price"] = fill_cost
        # self.set_current_holdings = fill, cost

    def update_fill(self, event: FillEvent) -> None:
        if event.get_event_type == "FILL":
            self.udate_positions_from_fill(event)
            self.update_holdings_from_fill(event)

    def generate_naive_order(self, signal: SignalEvent) -> OrderEvent:
        order = None
        symbol = signal.get_symbol
        direction = signal.get_signal_type
        strength = signal.get_strength
        timeindx = signal.get_datetime
        mkt_quantity = 1
        cur_quantity = self.get_current_positions[symbol]
        order_type = "MKT"

        if direction == "LONG" and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, "BUY", timeindx)
        if direction == "SHORT" and cur_quantity == 0:
            order = OrderEvent(symbol, order_type, mkt_quantity, "SELL", timeindx)

        if direction == "EXIT" and cur_quantity > 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), "SELL", timeindx)
        if direction == "EXIT" and cur_quantity < 0:
            order = OrderEvent(symbol, order_type, abs(cur_quantity), "BUY", timeindx)
        return order

    def update_signal(self, event: Event) -> None:
        if event.get_event_type == "SIGNAL":
            order_event = self.generate_naive_order(event)
            self.__events.put(order_event)

    def create_equity_curve_dataframe(self) -> None:
        curve = pd.DataFrame(self.get_all_holdings)
        # print(curve.tail(10))
        curve.set_index("datetime", inplace=True)
        curve["returns"] = curve["total"].pct_change()
        curve["equity_curve"] = (1.0 + curve["returns"]).cumprod()
        self.set_equity_curve = curve
    
    def output_summary_stats(self) -> list:
        total_return = self.get_equity_curve["equity_curve"].iloc[-1]
        returns = self.get_equity_curve["returns"]
        pnl = self.get_equity_curve["equity_curve"]
        sharp_ratio = create_sharp_ratio(returns, periods=252*60*6.5)
        drawdown, max_drawdown, dd_duration = create_drawdowns(pnl)
        # create_drawdowns(pnl)
        self.get_equity_curve["drawdown"] = drawdown

        # stats = 0
        stats = [("Total_return", "%0.2f%%" % ((total_return - 1.0) * 100.0)),
                ("Shape_ratio", "%0.2f" % sharp_ratio),
                ("Max Drawdown", "%0.2f%%" % (max_drawdown * 100.0)),
                ("Drawdown Duration", "%d" % dd_duration)]
        self.get_equity_curve.to_csv("equity.csv")
        return stats
