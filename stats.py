#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime


class stats(object):
    def __init__(self, stratagy_portfolio: list) -> None:
        self.__stratagy_portfolio = stratagy_portfolio
        self.__stratagy_names = [stratagy.get_stratagy_params["stratagy_name"] for stratagy in stratagy_portfolio]
        self.__symbol_list = self.__create_symbol_list()
        self.__stats_mode = self.__stratagy_portfolio[0].get_stratagy_params["args"]["args"].stats_mode
        self.__stats = self.__create_stats_structe()

    @property
    def get_stats(self) -> None:
        return self.__stats
    
    def __create_symbol_list(self) -> list:
        symbol_list = [stratagy.get_stratagy_params["symbol_list"] for stratagy in self.__stratagy_portfolio]
        symbol_list = [symbol for list_ in symbol_list for symbol in list_]
        symbol_list = list(set(symbol_list))
        return symbol_list
    
    def __create_stats_structe(self) -> dict:
        stats = {}
        # equity_curve_stats
        # stats["curve"] = {stratagy_name: {"capital": 0, "pnl": 0, "datetime": 0} for stratagy_name in self.__stratagy_names}
        # stats["curve"]["portfolio"] =  {"capital": 0, "pnl": 0, "datetime": 0}
        # portfolio_stats
        stats["portfolio"] = {stratagy_name: {} for stratagy_name in self.__stratagy_names}
        stats["portfolio"]["total"] = {"koefs": {}, "deals_stats": {}, "holdings_stats": {}}
        # deals_stats
        stats["portfolio"]["total"]["deals_stats"]["deals_count"] = 0
        stats["portfolio"]["total"]["deals_stats"]["deals_gross_pnl"] = 0
        stats["portfolio"]["total"]["deals_stats"]["commission"] = 0
        stats["portfolio"]["total"]["deals_stats"]["deals_pnl"] = 0
        # win_deals_stats
        stats["portfolio"]["total"]["deals_stats"]["win_deals_count"] = 0
        stats["portfolio"]["total"]["deals_stats"]["win_deals_gross_pnl"] = 0
        stats["portfolio"]["total"]["deals_stats"]["win_commission"] = 0
        stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"] = 0
        # loss_deals_stats
        stats["portfolio"]["total"]["deals_stats"]["loss_deals_count"] = 0
        stats["portfolio"]["total"]["deals_stats"]["loss_deals_gross_pnl"] = 0
        stats["portfolio"]["total"]["deals_stats"]["loss_commission"] = 0
        stats["portfolio"]["total"]["deals_stats"]["loss_deals_pnl"] = 0
        # holdings_stats
        stats["portfolio"]["total"]["holdings_stats"]["gross_pnl"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["commission"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["pnl"] = 0

        if self.__stats_mode == "full":
            # long_stats
            stats["portfolio"]["total"]["holdings_stats"]["long_gross_pnl"] = 0
            stats["portfolio"]["total"]["holdings_stats"]["long_commission"] = 0
            stats["portfolio"]["total"]["holdings_stats"]["long_pnl"] = 0
            # short_stats
            stats["portfolio"]["total"]["holdings_stats"]["short_gross_pnl"] = 0
            stats["portfolio"]["total"]["holdings_stats"]["short_commission"] = 0
            stats["portfolio"]["total"]["holdings_stats"]["short_pnl"] = 0

            stats["portfolio"]["total"]["holdings_stats"]["start_date"] = datetime.datetime.now()

        for symbol in self.__symbol_list:
            # for symbol in portfolio stats
            stats["portfolio"][symbol] = {}
            if self.__stats_mode == "full":
                stats["portfolio"][symbol]["koefs"] = {}
                # deals_stats
                stats["portfolio"][symbol]["deals_stats"] = {}
                stats["portfolio"][symbol]["deals_stats"]["deals_count"] = 0
                stats["portfolio"][symbol]["deals_stats"]["deals_gross_pnl"] = 0
                stats["portfolio"][symbol]["deals_stats"]["commission"] = 0
                stats["portfolio"][symbol]["deals_stats"]["deals_pnl"] = 0
                # win_deals_stats
                stats["portfolio"][symbol]["deals_stats"]["win_deals_count"] = 0
                stats["portfolio"][symbol]["deals_stats"]["win_deals_gross_pnl"] = 0
                stats["portfolio"][symbol]["deals_stats"]["win_commission"] = 0
                stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"] = 0
                # loss_deals_stats
                stats["portfolio"][symbol]["deals_stats"]["loss_deals_count"] = 0
                stats["portfolio"][symbol]["deals_stats"]["loss_deals_gross_pnl"] = 0
                stats["portfolio"][symbol]["deals_stats"]["loss_commission"] = 0
                stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"] = 0
                # holdings_stats
                stats["portfolio"][symbol]["holdings_stats"] = {}
                stats["portfolio"][symbol]["holdings_stats"]["gross_pnl"] = 0
                stats["portfolio"][symbol]["holdings_stats"]["commission"] = 0
                stats["portfolio"][symbol]["holdings_stats"]["pnl"] = 0
               
                if self.__stats_mode == "full":
                    # long_stats
                    stats["portfolio"][symbol]["holdings_stats"]["long_gross_pnl"] = 0
                    stats["portfolio"][symbol]["holdings_stats"]["long_commission"] = 0
                    stats["portfolio"][symbol]["holdings_stats"]["long_pnl"] = 0
                    # short_stats
                    stats["portfolio"][symbol]["holdings_stats"]["short_gross_pnl"] = 0
                    stats["portfolio"][symbol]["holdings_stats"]["short_commission"] = 0
                    stats["portfolio"][symbol]["holdings_stats"]["short_pnl"] = 0
        return stats
