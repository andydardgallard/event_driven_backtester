#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import datetime
from handler import convert_str_toDateTime

'''
Create performance stats of backtest
'''

class Metrics(object):
    def __init__(self) -> None:
       self.__metrics = {
            "duration": 0
        }
       
    @property
    def get_duration(self) -> datetime.timedelta:
        return self.__metrics["duration"]
    
    @get_duration.setter
    def set_duration(self, timedelta: datetime.timedelta) -> None:
        self.__metrics["duration"] = timedelta

metrics = Metrics()

def get_deal_stats(all_positions: dict, params_list: dict) -> dict:
    symbol_list = list(params_list["data_iter"].keys())
    stats_mode = params_list["args"]["args"].stats_mode
    initial_capital = params_list["initial_capital"]

    stats = {}
    stats["total"] = {}
    stats["total"]["koefs"] = {}
    stats["total"]["deals_stats"] = {}
    stats["total"]["deals_stats"]["deals_count"] = 0
    stats["total"]["deals_stats"]["deals_gross_pnl"] = 0
    stats["total"]["deals_stats"]["commission"] = 0
    stats["total"]["deals_stats"]["deals_pnl"] = 0
    stats["total"]["deals_stats"]["win_deals_count"] = 0
    stats["total"]["deals_stats"]["win_deals_gross_pnl"] = 0
    stats["total"]["deals_stats"]["win_commission"] = 0
    stats["total"]["deals_stats"]["win_deals_pnl"] = 0
    stats["total"]["deals_stats"]["loss_deals_count"] = 0
    stats["total"]["deals_stats"]["loss_deals_gross_pnl"] = 0
    stats["total"]["deals_stats"]["loss_commission"] = 0
    stats["total"]["deals_stats"]["loss_deals_pnl"] = 0

    for symbol in symbol_list:
        stats[symbol] = {}
        if stats_mode == "full":
            stats[symbol]["koefs"] = {}
        deals = []
        for pos in all_positions:
            deals.append(pos[symbol])
        deals = list({item["dealNumber"]: item for item in deals if item["dealNumber"] != None}.values())
    
        stats[symbol]["deals_stats"] = {}
        stats[symbol]["deals_stats"]["deals_count"] = len(deals)
        stats[symbol]["deals_stats"]["deals_gross_pnl"] = sum([i["dealGrossPnl"] for i in deals])
        stats[symbol]["deals_stats"]["commission"] = sum([i["entryCommission"] + i["exitCommission"] for i in deals])
        stats[symbol]["deals_stats"]["deals_pnl"] = sum([i["dealPnl"] for i in deals])
        stats[symbol]["deals_stats"]["deals_pnl"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["deals_pnl"]))
        if len(deals) > 0:
            stats[symbol]["deals_stats"]["deal_pnl_avrg"] = stats[symbol]["deals_stats"]["deals_pnl"] / stats[symbol]["deals_stats"]["deals_count"]
            stats[symbol]["deals_stats"]["deal_pnl_avrg"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["deal_pnl_avrg"]))
            stats[symbol]["deals_stats"]["deals_return"] = stats[symbol]["deals_stats"]["deals_pnl"] / deals[0]["entryCapital"]
            stats[symbol]["deals_stats"]["deals_return"] = float('{:.5f}'.format(stats[symbol]["deals_stats"]["deals_return"]))
            stats[symbol]["deals_stats"]["deals_return_avg"] = stats[symbol]["deals_stats"]["deals_return"] / stats[symbol]["deals_stats"]["deals_count"]
            stats[symbol]["deals_stats"]["deals_return_avg"] = float('{:.5f}'.format(stats[symbol]["deals_stats"]["deals_return_avg"]))
        else:
            stats[symbol]["deals_stats"]["deal_pnl_avrg"] = 0
            stats[symbol]["deals_stats"]["deals_return"] = 0 
            stats[symbol]["deals_stats"]["deals_return_avg"] = 0

        win_deals = [i["dealPnl"] for i in deals if i["dealPnl"] > 0]
        stats[symbol]["deals_stats"]["win_deals_count"] = len(win_deals)
        stats[symbol]["deals_stats"]["win_deals_gross_pnl"] = sum([i["dealGrossPnl"] for i in deals if i["dealPnl"] > 0])
        stats[symbol]["deals_stats"]["win_commission"] = sum([i["entryCommission"] + i["exitCommission"] for i in deals if i["dealPnl"] > 0])
        stats[symbol]["deals_stats"]["win_deals_pnl"] = sum([i["dealPnl"] for i in deals if i["dealPnl"] > 0])
        stats[symbol]["deals_stats"]["win_deals_pnl"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["win_deals_pnl"]))
        if len(win_deals) > 0:
            stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] = stats[symbol]["deals_stats"]["win_deals_pnl"] / stats[symbol]["deals_stats"]["win_deals_count"]
            stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["win_deal_pnl_avrg"]))
        else:
            stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] = 0.0

        loss_deals = [i["dealPnl"] for i in deals if i["dealPnl"] <= 0]
        stats[symbol]["deals_stats"]["loss_deals_count"] = len(loss_deals)
        stats[symbol]["deals_stats"]["loss_deals_gross_pnl"] = sum([i["dealGrossPnl"] for i in deals if i["dealPnl"] <= 0])
        stats[symbol]["deals_stats"]["loss_commission"] = sum([i["entryCommission"] + i["exitCommission"] for i in deals if i["dealPnl"] <= 0])
        stats[symbol]["deals_stats"]["loss_commission"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["loss_commission"]))
        stats[symbol]["deals_stats"]["loss_deals_pnl"] = sum([i["dealPnl"] for i in deals if i["dealPnl"] <= 0])
        stats[symbol]["deals_stats"]["loss_deals_pnl"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["loss_deals_pnl"]))
        if len(loss_deals) > 0:
            stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"] = stats[symbol]["deals_stats"]["loss_deals_pnl"] / stats[symbol]["deals_stats"]["loss_deals_count"]
            stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"] = float('{:.3f}'.format(stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"]))
        else:
            stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"] = 0.0
        
        stats["total"]["deals_stats"]["deals_count"] += stats[symbol]["deals_stats"]["deals_count"]
        stats["total"]["deals_stats"]["deals_gross_pnl"] += stats[symbol]["deals_stats"]["deals_gross_pnl"]
        stats["total"]["deals_stats"]["commission"] += stats[symbol]["deals_stats"]["commission"]
        stats["total"]["deals_stats"]["deals_pnl"] += stats[symbol]["deals_stats"]["deals_pnl"]
        stats["total"]["deals_stats"]["deals_pnl"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["deals_pnl"]))
        if stats["total"]["deals_stats"]["deals_count"] > 0: 
            stats["total"]["deals_stats"]["deal_pnl_avrg"] = stats["total"]["deals_stats"]["deals_pnl"] / stats["total"]["deals_stats"]["deals_count"]
            stats["total"]["deals_stats"]["deal_pnl_avrg"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["deal_pnl_avrg"]))
            stats['total']["deals_stats"]["deals_return"] = stats["total"]["deals_stats"]["deals_pnl"] / initial_capital
            stats["total"]["deals_stats"]["deals_return"] = float('{:.5f}'.format(stats["total"]["deals_stats"]["deals_return"]))
            stats["total"]["deals_stats"]["deals_return_avg"] = stats["total"]["deals_stats"]["deals_return"] / stats["total"]["deals_stats"]["deals_count"]
            stats["total"]["deals_stats"]["deals_return_avg"] = float('{:.5f}'.format(stats["total"]["deals_stats"]["deals_return_avg"]))
        else:
            stats["total"]["deals_stats"]["deal_pnl_avrg"] = 0.0
            stats['total']["deals_stats"]["deals_return"] = 0.0
            stats["total"]["deals_stats"]["deals_return_avg"] = 0.0

        stats["total"]["deals_stats"]["win_deals_count"] += stats[symbol]["deals_stats"]["win_deals_count"]
        stats["total"]["deals_stats"]["win_deals_gross_pnl"] += stats[symbol]["deals_stats"]["win_deals_gross_pnl"]
        stats["total"]["deals_stats"]["win_commission"] += stats[symbol]["deals_stats"]["win_commission"]
        stats["total"]["deals_stats"]["win_deals_pnl"] += stats[symbol]["deals_stats"]["win_deals_pnl"]
        stats["total"]["deals_stats"]["win_deals_pnl"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["win_deals_pnl"]))
        if stats["total"]["deals_stats"]["win_deals_count"] > 0:
            stats["total"]["deals_stats"]["win_deal_pnl_avrg"] = stats["total"]["deals_stats"]["win_deals_pnl"] / stats["total"]["deals_stats"]["win_deals_count"]
            stats["total"]["deals_stats"]["win_deal_pnl_avrg"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["win_deal_pnl_avrg"]))
        else:
            stats["total"]["deals_stats"]["win_deal_pnl_avrg"] = 0
        
        stats["total"]["deals_stats"]["loss_deals_count"] += stats[symbol]["deals_stats"]["loss_deals_count"]
        stats["total"]["deals_stats"]["loss_deals_gross_pnl"] += stats[symbol]["deals_stats"]["loss_deals_gross_pnl"]
        stats["total"]["deals_stats"]["loss_commission"] += stats[symbol]["deals_stats"]["loss_commission"]
        stats["total"]["deals_stats"]["loss_commission"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["loss_commission"]))
        stats["total"]["deals_stats"]["loss_deals_pnl"] += stats[symbol]["deals_stats"]["loss_deals_pnl"]
        stats["total"]["deals_stats"]["loss_deals_pnl"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["loss_deals_pnl"]))
        if stats["total"]["deals_stats"]["loss_deals_count"] > 0:
            stats["total"]["deals_stats"]["loss_deal_pnl_avrg"] = stats["total"]["deals_stats"]["loss_deals_pnl"] / stats["total"]["deals_stats"]["loss_deals_count"]
            stats["total"]["deals_stats"]["loss_deal_pnl_avrg"] = float('{:.3f}'.format(stats["total"]["deals_stats"]["loss_deal_pnl_avrg"]))
        else:
            stats["total"]["deals_stats"]["loss_deal_pnl_avrg"] = 0
    return stats

def get_portfolio_deals_stats(stats: dict, stratagy) -> dict:
    stats = stats.get_stats
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stratagy_name = stratagy.get_stratagy_params["stratagy_name"]
    initial_capital = stratagy.get_stratagy_params["initial_capital"]
    
    for symbol in symbol_list:
        stats["portfolio"][symbol]["deals_stats"]["deals_count"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["deals_count"]
        stats["portfolio"][symbol]["deals_stats"]["deals_gross_pnl"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["deals_gross_pnl"]
        stats["portfolio"][symbol]["deals_stats"]["commission"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["commission"]
        stats["portfolio"][symbol]["deals_stats"]["deals_pnl"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["deals_pnl"]
        stats["portfolio"][symbol]["deals_stats"]["deals_pnl"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["deals_pnl"]))
        if stats["portfolio"][symbol]["deals_stats"]["deals_count"] > 0:
            stats["portfolio"][symbol]["deals_stats"]["deal_pnl_avrg"] = stats["portfolio"][symbol]["deals_stats"]["deals_pnl"] / stats["portfolio"][symbol]["deals_stats"]["deals_count"]
            stats["portfolio"][symbol]["deals_stats"]["deal_pnl_avrg"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["deal_pnl_avrg"]))
            stats["portfolio"][symbol]["deals_stats"]["deals_return"] = stats["portfolio"][symbol]["deals_stats"]["deals_pnl"] / initial_capital
            stats["portfolio"][symbol]["deals_stats"]["deals_return"] = float('{:.5f}'.format(stats["portfolio"][symbol]["deals_stats"]["deals_return"]))
            stats["portfolio"][symbol]["deals_stats"]["deals_return_avg"] = stats["portfolio"][symbol]["deals_stats"]["deals_return"] / stats["portfolio"][symbol]["deals_stats"]["deals_count"]
            stats["portfolio"][symbol]["deals_stats"]["deals_return_avg"] = float('{:.5f}'.format(stats["portfolio"][symbol]["deals_stats"]["deals_return_avg"]))
        else:
            stats["portfolio"][symbol]["deals_stats"]["deal_pnl_avrg"] = 0
            stats["portfolio"][symbol]["deals_stats"]["deals_return"] = 0 
            stats["portfolio"][symbol]["deals_stats"]["deals_return_avg"] = 0

        stats["portfolio"][symbol]["deals_stats"]["win_deals_count"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["win_deals_count"]
        stats["portfolio"][symbol]["deals_stats"]["win_deals_gross_pnl"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["win_deals_gross_pnl"]
        stats["portfolio"][symbol]["deals_stats"]["win_commission"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["win_commission"]
        stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["win_deals_pnl"]
        stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"]))
        if stats["portfolio"][symbol]["deals_stats"]["win_deals_count"] > 0:
            stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] = stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"] / stats["portfolio"][symbol]["deals_stats"]["win_deals_count"]
            stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"]))
        else:
            stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] = 0.0   
            
        stats["portfolio"][symbol]["deals_stats"]["loss_deals_count"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["win_deals_count"]
        stats["portfolio"][symbol]["deals_stats"]["loss_deals_gross_pnl"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["loss_deals_gross_pnl"]
        stats["portfolio"][symbol]["deals_stats"]["loss_commission"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["loss_commission"]
        stats["portfolio"][symbol]["deals_stats"]["loss_commission"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["loss_commission"]))
        stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"] += stats["portfolio"][stratagy_name][symbol]["deals_stats"]["loss_deals_pnl"]
        stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"]))
        if stats["portfolio"][symbol]["deals_stats"]["loss_deals_count"] > 0:
            stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"] = stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"] / stats["portfolio"][symbol]["deals_stats"]["loss_deals_count"]
            stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"] = float('{:.3f}'.format(stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"]))
        else:
            stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"] = 0.0  

    stats["portfolio"]["total"]["deals_stats"]["deals_count"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["deals_count"]
    stats["portfolio"]["total"]["deals_stats"]["deals_gross_pnl"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["deals_gross_pnl"]
    stats["portfolio"]["total"]["deals_stats"]["commission"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["commission"]
    stats["portfolio"]["total"]["deals_stats"]["deals_pnl"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["deals_pnl"]
    stats["portfolio"]["total"]["deals_stats"]["deals_pnl"] = float('{:.3f}'.format(stats["portfolio"]["total"]["deals_stats"]["deals_pnl"]))
    if stats["portfolio"]["total"]["deals_stats"]["deals_count"] > 0: 
        stats["portfolio"]["total"]["deals_stats"]["deal_pnl_avrg"] = stats["portfolio"]["total"]["deals_stats"]["deals_pnl"] / stats["portfolio"]["total"]["deals_stats"]["deals_count"]
        stats["portfolio"]["total"]["deals_stats"]["deal_pnl_avrg"] = float('{:.3f}'.format(stats["portfolio"]["total"]["deals_stats"]["deal_pnl_avrg"]))
        stats["portfolio"]['total']["deals_stats"]["deals_return"] = stats["portfolio"]["total"]["deals_stats"]["deals_pnl"] / initial_capital
        stats["portfolio"]["total"]["deals_stats"]["deals_return"] = float('{:.5f}'.format(stats["portfolio"]["total"]["deals_stats"]["deals_return"]))
        stats["portfolio"]["total"]["deals_stats"]["deals_return_avg"] = stats["portfolio"]["total"]["deals_stats"]["deals_return"] / stats["portfolio"]["total"]["deals_stats"]["deals_count"]
        stats["portfolio"]["total"]["deals_stats"]["deals_return_avg"] = float('{:.5f}'.format(stats["portfolio"]["total"]["deals_stats"]["deals_return_avg"]))
    else:
        stats["portfolio"]["total"]["deals_stats"]["deal_pnl_avrg"] = 0.0
        stats["portfolio"]['total']["deals_stats"]["deals_return"] = 0.0
        stats["portfolio"]["total"]["deals_stats"]["deals_return_avg"] = 0.0

    stats["portfolio"]["total"]["deals_stats"]["win_deals_count"]  += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["win_deals_count"]
    stats["portfolio"]["total"]["deals_stats"]["win_deals_gross_pnl"]  += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["win_deals_gross_pnl"]
    stats["portfolio"]["total"]["deals_stats"]["win_commission"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["win_commission"]
    stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["win_deals_pnl"]
    stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"] = float('{:.3f}'.format(stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"]))
    if stats["portfolio"]["total"]["deals_stats"]["win_deals_count"] > 0:
        stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] = stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"] / stats["portfolio"]["total"]["deals_stats"]["win_deals_count"]
        stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] = float('{:.3f}'.format(stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"]))
    else:
        stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] = 0
    
    stats["portfolio"]["total"]["deals_stats"]["loss_deals_count"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["loss_deals_count"]
    stats["portfolio"]["total"]["deals_stats"]["loss_deals_gross_pnl"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["loss_deals_gross_pnl"]
    stats["portfolio"]["total"]["deals_stats"]["loss_commission"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["loss_commission"]
    stats["portfolio"]["total"]["deals_stats"]["loss_commission"] = float('{:.3f}'.format(stats["portfolio"]["total"]["deals_stats"]["loss_commission"]))
    stats["portfolio"]["total"]["deals_stats"]["loss_deals_pnl"] += stats["portfolio"][stratagy_name]["total"]["deals_stats"]["loss_deals_pnl"]    
    if stats["portfolio"]["total"]["deals_stats"]["loss_deals_count"] > 0:
        stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"] = stats["portfolio"]["total"]["deals_stats"]["loss_deals_pnl"] / stats["portfolio"]["total"]["deals_stats"]["loss_deals_count"]
        stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"] = float('{:.3f}'.format(stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"]))
    else:
        stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"] = 0

def calculate_winRate(stats: dict, symbol_list: list, stats_mode: str) -> dict:
    if stats_mode == "full":
        for symbol in symbol_list:
            if stats[symbol]["deals_stats"]["deals_count"] > 0:
                stats[symbol]["koefs"]["win_rate"] = stats[symbol]["deals_stats"]["win_deals_count"] / stats[symbol]["deals_stats"]["deals_count"]
                stats[symbol]["koefs"]["win_rate"] = float('{:.5f}'.format(stats[symbol]["koefs"]["win_rate"]))
            else:
                stats[symbol]["koefs"]["win_rate"] = 0
    if stats["total"]["deals_stats"]["deals_count"] > 0:
        stats["total"]["koefs"]["win_rate"] = stats["total"]["deals_stats"]["win_deals_count"] / stats["total"]["deals_stats"]["deals_count"]
        stats["total"]["koefs"]["win_rate"] = float('{:.5f}'.format(stats["total"]["koefs"]["win_rate"]))
    else:
        stats["total"]["koefs"]["win_rate"] = 0
    return stats

def calculate_portfolio_winRate(stats: dict, stratagy) -> dict:
    stats_mode = stratagy.get_stratagy_params["args"]["args"].stats_mode
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stats = stats.get_stats

    if stats_mode == "full":
        for symbol in symbol_list:
            if stats["portfolio"][symbol]["deals_stats"]["deals_count"] > 0:
                stats["portfolio"][symbol]["koefs"]["win_rate"] = stats["portfolio"][symbol]["deals_stats"]["win_deals_count"] / stats["portfolio"][symbol]["deals_stats"]["deals_count"]
                stats["portfolio"][symbol]["koefs"]["win_rate"] = float('{:.5f}'.format(stats["portfolio"][symbol]["koefs"]["win_rate"]))
            else:
                stats["portfolio"][symbol]["koefs"]["win_rate"] = 0
    if stats["portfolio"]["total"]["deals_stats"]["deals_count"] > 0:
        stats["portfolio"]["total"]["koefs"]["win_rate"] = stats["portfolio"]["total"]["deals_stats"]["win_deals_count"] / stats["portfolio"]["total"]["deals_stats"]["deals_count"]
        stats["portfolio"]["total"]["koefs"]["win_rate"] = float('{:.5f}'.format(stats["portfolio"]["total"]["koefs"]["win_rate"]))
    else:
        stats["portfolio"]["total"]["koefs"]["win_rate"] = 0

def calculate_expected_payoff(stats: dict, symbol_list: list, stats_mode: str) -> dict:
    if stats_mode == "full":
        for symbol in symbol_list:
            if stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] != 0 and stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"]:
                stats[symbol]["koefs"]["expected_payoff"] = stats[symbol]["koefs"]["win_rate"] * stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] \
                                                        + (1 - stats[symbol]["koefs"]["win_rate"]) * stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"] 
                stats[symbol]["koefs"]["expected_payoff"] = float('{:.3f}'.format(stats[symbol]["koefs"]["expected_payoff"]))
                stats[symbol]["koefs"]["expected_payoff_probability"] = ((1 + (stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"]))) \
                                                        * stats[symbol]["koefs"]["win_rate"]) - 1
                stats[symbol]["koefs"]["expected_payoff_probability"] = float('{:.5f}'.format(stats[symbol]["koefs"]["expected_payoff_probability"]))
            else:
                stats[symbol]["koefs"]["expected_payoff"] = None
                stats[symbol]["koefs"]["expected_payoff_probability"] = None

    stats["total"]["koefs"]["expected_payoff"] = stats["total"]["koefs"]["win_rate"] * stats["total"]["deals_stats"]["win_deal_pnl_avrg"] \
                                            + (1 - stats["total"]["koefs"]["win_rate"]) * stats["total"]["deals_stats"]["loss_deal_pnl_avrg"]
    stats["total"]["koefs"]["expected_payoff"] = float('{:.3f}'.format(stats["total"]["koefs"]["expected_payoff"]))
    if stats["total"]["deals_stats"]["loss_deal_pnl_avrg"]:
        stats["total"]["koefs"]["expected_payoff_probability"] = ((1 + (stats["total"]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["total"]["deals_stats"]["loss_deal_pnl_avrg"]))) \
                                                * stats["total"]["koefs"]["win_rate"]) - 1
        stats["total"]["koefs"]["expected_payoff_probability"] = float('{:.5f}'.format(stats["total"]["koefs"]["expected_payoff_probability"]))
    else:
        stats["total"]["koefs"]["expected_payoff_probability"] = 0
    return stats

def calculate_portfolio_expected_payoff(stats: dict, stratagy) -> dict:
    stats_mode = stratagy.get_stratagy_params["args"]["args"].stats_mode
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stats = stats.get_stats

    if stats_mode == "full":
        for symbol in symbol_list:
            if stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] != 0 and stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"]:
                stats["portfolio"][symbol]["koefs"]["expected_payoff"] = stats["portfolio"][symbol]["koefs"]["win_rate"] * stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] \
                                                        + (1 - stats["portfolio"][symbol]["koefs"]["win_rate"]) * stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"] 
                stats["portfolio"][symbol]["koefs"]["expected_payoff"] = float('{:.3f}'.format(stats["portfolio"][symbol]["koefs"]["expected_payoff"]))
                stats["portfolio"][symbol]["koefs"]["expected_payoff_probability"] = ((1 + (stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"]))) \
                                                        * stats["portfolio"][symbol]["koefs"]["win_rate"]) - 1
                stats["portfolio"][symbol]["koefs"]["expected_payoff_probability"] = float('{:.5f}'.format(stats["portfolio"][symbol]["koefs"]["expected_payoff_probability"]))
            else:
                stats["portfolio"][symbol]["koefs"]["expected_payoff"] = None
                stats["portfolio"][symbol]["koefs"]["expected_payoff_probability"] = None

    stats["portfolio"]["total"]["koefs"]["expected_payoff"] = stats["portfolio"]["total"]["koefs"]["win_rate"] * stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] \
                                            + (1 - stats["portfolio"]["total"]["koefs"]["win_rate"]) * stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"]
    stats["portfolio"]["total"]["koefs"]["expected_payoff"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["expected_payoff"]))
    if stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"]:
        stats["portfolio"]["total"]["koefs"]["expected_payoff_probability"] = ((1 + (stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"]))) \
                                                * stats["portfolio"]["total"]["koefs"]["win_rate"]) - 1
        stats["portfolio"]["total"]["koefs"]["expected_payoff_probability"] = float('{:.5f}'.format(stats["portfolio"]["total"]["koefs"]["expected_payoff_probability"]))
    else:
        stats["portfolio"]["total"]["koefs"]["expected_payoff_probability"] = 0

def calculate_breakeven(stats: dict, symbol_list: list, stats_mode: str) -> dict:
    if stats_mode == "full":
        for symbol in symbol_list:
            if stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"] and stats[symbol]["deals_stats"]["win_deals_count"]:
                stats[symbol]["koefs"]["breakeven"] = (stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                    - (stats[symbol]["deals_stats"]["loss_deals_count"] / stats[symbol]["deals_stats"]["win_deals_count"])
                stats[symbol]["koefs"]["breakeven"] = float('{:.5f}'.format(stats[symbol]["koefs"]["breakeven"]))
            else:
                stats[symbol]["koefs"]["breakeven"] = None
    if stats["total"]["deals_stats"]["win_deals_count"] > 0 and stats["total"]["deals_stats"]["loss_deal_pnl_avrg"]:
        stats["total"]["koefs"]["breakeven"] = (stats["total"]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["total"]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                - (stats["total"]["deals_stats"]["loss_deals_count"] / stats["total"]["deals_stats"]["win_deals_count"])
        stats["total"]["koefs"]["breakeven"] = float('{:.5f}'.format(stats["total"]["koefs"]["breakeven"]))
    else:
        stats["total"]["koefs"]["breakeven"] = None
    return stats

def calculate_portfolio_breakeven(stats: dict, stratagy) -> dict:
    stats_mode = stratagy.get_stratagy_params["args"]["args"].stats_mode
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stats = stats.get_stats

    if stats_mode == "full":
        for symbol in symbol_list:
            if stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"]:
                stats["portfolio"][symbol]["koefs"]["breakeven"] = (stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                    - (stats["portfolio"][symbol]["deals_stats"]["loss_deals_count"] / stats["portfolio"][symbol]["deals_stats"]["win_deals_count"])
                stats["portfolio"][symbol]["koefs"]["breakeven"] = float('{:.5f}'.format(stats["portfolio"][symbol]["koefs"]["breakeven"]))
            else:
                stats["portfolio"][symbol]["koefs"]["breakeven"] = None
    if stats["portfolio"]["total"]["deals_stats"]["win_deals_count"] > 0 and stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"]:
        stats["portfolio"]["total"]["koefs"]["breakeven"] = (stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                - (stats["portfolio"]["total"]["deals_stats"]["loss_deals_count"] / stats["portfolio"]["total"]["deals_stats"]["win_deals_count"])
        stats["portfolio"]["total"]["koefs"]["breakeven"] = float('{:.5f}'.format(stats["portfolio"]["total"]["koefs"]["breakeven"]))
    else:
        stats["portfolio"]["total"]["koefs"]["breakeven"] = None

def calculate_breakeven_with_tradeoff(stats: dict, symbol_list: list, tradeoff: float, stats_mode: str) -> dict:
    if stats_mode == "full":
        for symbol in symbol_list:
            if stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"] and stats[symbol]["deals_stats"]["win_deals_count"]:
                stats[symbol]["koefs"]["breakeven_tradeoff"] = (stats[symbol]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats[symbol]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                            - (1 / (stats[symbol]["koefs"]["win_rate"] - tradeoff))
                stats[symbol]["koefs"]["breakeven_tradeoff"] = float('{:.3f}'.format(stats[symbol]["koefs"]["breakeven_tradeoff"]))
            else:
                stats[symbol]["koefs"]["breakeven_tradeoff"] = None
    if stats["total"]["deals_stats"]["loss_deal_pnl_avrg"]:
        stats["total"]["koefs"]["breakeven_tradeoff"] = (stats["total"]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["total"]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                        - (1 / (stats["total"]["koefs"]["win_rate"] - tradeoff))
        stats["total"]["koefs"]["breakeven_tradeoff"] = float('{:.3f}'.format(stats["total"]["koefs"]["breakeven_tradeoff"]))
    else:
        stats["total"]["koefs"]["breakeven_tradeoff"] = 0
    return stats

def calculate_portfolio_breakeven_with_tradeoff(stats: dict, stratagy, tradeoff: float) -> dict:
    stats_mode = stratagy.get_stratagy_params["args"]["args"].stats_mode
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stats = stats.get_stats

    if stats_mode == "full":
        for symbol in symbol_list:
            if stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"]:
                stats["portfolio"][symbol]["koefs"]["breakeven_tradeoff"] = (stats["portfolio"][symbol]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["portfolio"][symbol]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                            - (1 / (stats["portfolio"][symbol]["koefs"]["win_rate"] - tradeoff))
                stats["portfolio"][symbol]["koefs"]["breakeven_tradeoff"] = float('{:.3f}'.format(stats["portfolio"][symbol]["koefs"]["breakeven_tradeoff"]))
            else:
                stats["portfolio"][symbol]["koefs"]["breakeven_tradeoff"] = None
    if stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"]:
        stats["portfolio"]["total"]["koefs"]["breakeven_tradeoff"] = (stats["portfolio"]["total"]["deals_stats"]["win_deal_pnl_avrg"] / abs(stats["portfolio"]["total"]["deals_stats"]["loss_deal_pnl_avrg"])) \
                                                        - (1 / (stats["portfolio"]["total"]["koefs"]["win_rate"] - tradeoff))
        stats["portfolio"]["total"]["koefs"]["breakeven_tradeoff"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["breakeven_tradeoff"]))
    else:
        stats["portfolio"]["total"]["koefs"]["breakeven_tradeoff"] = 0

def calculate_profit_factor(stats: dict, symbol_list: list, stats_mode: str) -> dict:
    if stats_mode == "full":
        for symbol in symbol_list:
            if stats[symbol]["deals_stats"]["loss_deals_pnl"] != 0:
                stats[symbol]["koefs"]["profit_factor"] = stats[symbol]["deals_stats"]["win_deals_pnl"] / abs(stats[symbol]["deals_stats"]["loss_deals_pnl"])
                stats[symbol]["koefs"]["profit_factor"] = float('{:.3f}'.format(stats[symbol]["koefs"]["profit_factor"]))
            else:
                stats[symbol]["koefs"]["profit_factor"] = None
    if stats["total"]["deals_stats"]["loss_deals_pnl"]:
        stats["total"]["koefs"]["profit_factor"] = stats["total"]["deals_stats"]["win_deals_pnl"] / abs(stats["total"]["deals_stats"]["loss_deals_pnl"])
        stats["total"]["koefs"]["profit_factor"] = float('{:.3f}'.format(stats["total"]["koefs"]["profit_factor"]))
    else:
        stats["total"]["koefs"]["profit_factor"] = 0
    return stats

def calculate_portfolio_profit_factor(stats: dict, stratagy) -> dict:
    stats_mode = stratagy.get_stratagy_params["args"]["args"].stats_mode
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stats = stats.get_stats

    if stats_mode == "full":
        for symbol in symbol_list:
            if stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"] != 0:
                stats["portfolio"][symbol]["koefs"]["profit_factor"] = stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"] / abs(stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"])
                stats["portfolio"][symbol]["koefs"]["profit_factor"] = float('{:.3f}'.format(stats["portfolio"][symbol]["koefs"]["profit_factor"]))
            else:
                stats["portfolio"][symbol]["koefs"]["profit_factor"] = None
    if stats["portfolio"]["total"]["deals_stats"]["loss_deals_pnl"]:
        stats["portfolio"]["total"]["koefs"]["profit_factor"] = stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"] / abs(stats["portfolio"]["total"]["deals_stats"]["loss_deals_pnl"])
        stats["portfolio"]["total"]["koefs"]["profit_factor"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["profit_factor"]))
    else:
        stats["portfolio"]["total"]["koefs"]["profit_factor"] = 0

def get_holdings_stats(stats: dict, all_holdings: dict, symbol_list: list, last_bar_datetime: datetime.datetime, stats_mode: str) -> dict:
    start_date = None
    for i in all_holdings:
        if not start_date and i["datetime"]:
            start_date = i["datetime"]
    metrics.set_duration = last_bar_datetime - start_date

    stats["total"]["holdings_stats"] = {}
    stats["total"]["holdings_stats"]["gross_pnl"] = 0
    stats["total"]["holdings_stats"]["commission"] = 0
    stats["total"]["holdings_stats"]["pnl"] = 0
    if stats_mode == "full":
        stats["total"]["holdings_stats"]["long_gross_pnl"] = 0
        stats["total"]["holdings_stats"]["long_commission"] = 0
        stats["total"]["holdings_stats"]["long_pnl"] = 0
        stats["total"]["holdings_stats"]["short_gross_pnl"] = 0
        stats["total"]["holdings_stats"]["short_commission"] = 0
        stats["total"]["holdings_stats"]["short_pnl"] = 0
    
    for symbol in symbol_list:
        stats[symbol]["holdings_stats"] = {}
        stats[symbol]["holdings_stats"]["gross_pnl"] = sum([i[symbol]["grossPnl"] for i in all_holdings if i[symbol]["grossPnl"] != 0])
        stats[symbol]["holdings_stats"]["commission"] = sum([i[symbol]["commission"] for i in all_holdings if i[symbol]["commission"] != 0])
        stats[symbol]["holdings_stats"]["pnl"] = sum([i[symbol]["pnl"] for i in all_holdings])
        stats[symbol]["holdings_stats"]["pnl"] = float('{:.3f}'.format(stats[symbol]["holdings_stats"]["pnl"]))
        if stats_mode == "full":
            stats[symbol]["holdings_stats"]["long_gross_pnl"] = sum([i[symbol]["longGrossPnl"] for i in all_holdings if i[symbol]["longGrossPnl"] != 0])
            stats[symbol]["holdings_stats"]["long_commission"] = sum([i[symbol]["commission"] for i in all_holdings if i[symbol]["longCommission"] != 0])
            stats[symbol]["holdings_stats"]["long_commission"] = float('{:.3f}'.format(stats[symbol]["holdings_stats"]["long_commission"]))
            stats[symbol]["holdings_stats"]["long_pnl"] = sum([i[symbol]["longPnl"] for i in all_holdings if i[symbol]["longPnl"] != 0])
            stats[symbol]["holdings_stats"]["long_pnl"] = float('{:.3f}'.format(stats[symbol]["holdings_stats"]["long_pnl"]))
            stats[symbol]["holdings_stats"]["short_gross_pnl"] = sum([i[symbol]["shortGrossPnl"] for i in all_holdings if i[symbol]["shortGrossPnl"] != 0])
            stats[symbol]["holdings_stats"]["short_commission"] = sum([i[symbol]["commission"] for i in all_holdings if i[symbol]["shortCommission"] != 0])
            stats[symbol]["holdings_stats"]["short_pnl"] = sum([i[symbol]["shortPnl"] for i in all_holdings if i[symbol]["shortPnl"] != 0])
            stats[symbol]["holdings_stats"]["short_pnl"] = float('{:.3f}'.format(stats[symbol]["holdings_stats"]["short_pnl"]))

        stats["total"]["holdings_stats"]["gross_pnl"] += stats[symbol]["holdings_stats"]["gross_pnl"]
        stats["total"]["holdings_stats"]["commission"] += stats[symbol]["holdings_stats"]["commission"]
        stats["total"]["holdings_stats"]["pnl"] += stats[symbol]["holdings_stats"]["pnl"]
        stats["total"]["holdings_stats"]["pnl"] = float('{:.3f}'.format(stats["total"]["holdings_stats"]["pnl"]))
        if stats_mode == "full":
            stats["total"]["holdings_stats"]["long_gross_pnl"] += stats[symbol]["holdings_stats"]["long_gross_pnl"]
            stats["total"]["holdings_stats"]["long_commission"] += stats[symbol]["holdings_stats"]["long_commission"]
            stats["total"]["holdings_stats"]["long_pnl"] += stats[symbol]["holdings_stats"]["long_pnl"]
            stats["total"]["holdings_stats"]["short_gross_pnl"] += stats[symbol]["holdings_stats"]["short_gross_pnl"]
            stats["total"]["holdings_stats"]["short_commission"] += stats[symbol]["holdings_stats"]["short_commission"]
            stats["total"]["holdings_stats"]["short_pnl"] += stats[symbol]["holdings_stats"]["short_pnl"]
        stats["total"]["holdings_stats"]["duration"] = (str(metrics.get_duration)).split(',')[0]
        stats["total"]["holdings_stats"]["start_date"] = f'{start_date:%Y-%m-%d %H:%M:%S}'
        stats["total"]["holdings_stats"]["last_bar_datetime"] = f'{last_bar_datetime:%Y-%m-%d %H:%M:%S}'
    return stats

def get_portfolio_holdings_stats(stats: dict, stratagy) -> dict:
    stats_mode = stratagy.get_stratagy_params["args"]["args"].stats_mode
    symbol_list = stratagy.get_stratagy_params["symbol_list"]
    stats = stats.get_stats
    stratagy_name = stratagy.get_stratagy_params["stratagy_name"]

    for symbol in symbol_list:
        stats["portfolio"][symbol]["holdings_stats"]["gross_pnl"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["gross_pnl"]
        stats["portfolio"][symbol]["holdings_stats"]["commission"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["commission"]
        stats["portfolio"][symbol]["holdings_stats"]["pnl"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["pnl"]
        stats["portfolio"][symbol]["holdings_stats"]["pnl"] = float('{:.3f}'.format(stats["portfolio"][symbol]["holdings_stats"]["pnl"]))

        if stats_mode == "full":
            stats["portfolio"][symbol]["holdings_stats"]["long_gross_pnl"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["long_gross_pnl"]
            stats["portfolio"][symbol]["holdings_stats"]["long_commission"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["long_commission"]
            stats["portfolio"][symbol]["holdings_stats"]["long_pnl"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["long_pnl"]
            stats["portfolio"][symbol]["holdings_stats"]["long_pnl"] = float('{:.3f}'.format(stats["portfolio"][symbol]["holdings_stats"]["long_pnl"]))

            stats["portfolio"][symbol]["holdings_stats"]["short_gross_pnl"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["short_gross_pnl"]
            stats["portfolio"][symbol]["holdings_stats"]["short_commission"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["short_commission"]
            stats["portfolio"][symbol]["holdings_stats"]["short_pnl"] += stats["portfolio"][stratagy_name][symbol]["holdings_stats"]["short_pnl"]
            stats["portfolio"][symbol]["holdings_stats"]["short_pnl"] = float('{:.3f}'.format(stats["portfolio"][symbol]["holdings_stats"]["short_pnl"]))
    
    stats["portfolio"]["total"]["holdings_stats"]["gross_pnl"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["gross_pnl"]
    stats["portfolio"]["total"]["holdings_stats"]["commission"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["commission"]
    stats["portfolio"]["total"]["holdings_stats"]["pnl"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["pnl"]
    stats["portfolio"]["total"]["holdings_stats"]["pnl"] = float('{:.3f}'.format(stats["portfolio"]["total"]["holdings_stats"]["pnl"]))
    if stats_mode == "full":
        stats["portfolio"]["total"]["holdings_stats"]["long_gross_pnl"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["long_gross_pnl"]
        stats["portfolio"]["total"]["holdings_stats"]["long_commission"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["long_commission"]
        stats["portfolio"]["total"]["holdings_stats"]["long_pnl"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["long_pnl"]
        stats["portfolio"]["total"]["holdings_stats"]["long_pnl"] = float('{:.3f}'.format(stats["portfolio"]["total"]["holdings_stats"]["long_pnl"]))
        stats["portfolio"]["total"]["holdings_stats"]["short_gross_pnl"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["short_gross_pnl"]
        stats["portfolio"]["total"]["holdings_stats"]["short_commission"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["short_commission"]
        stats["portfolio"]["total"]["holdings_stats"]["short_pnl"] += stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["short_pnl"]
        
        stats["portfolio"]["total"]["holdings_stats"]["start_date"] = convert_str_toDateTime(stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["start_date"]) \
            if convert_str_toDateTime(stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["start_date"]) < stats["portfolio"]["total"]["holdings_stats"]["start_date"] \
            else stats["portfolio"]["total"]["holdings_stats"]["start_date"]
        
        stats["portfolio"]["total"]["holdings_stats"]["last_bar_datetime"] = stats["portfolio"]["total"]["holdings_stats"]["start_date"]
        stats["portfolio"]["total"]["holdings_stats"]["last_bar_datetime"] = convert_str_toDateTime(stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["last_bar_datetime"]) \
            if convert_str_toDateTime(stats["portfolio"][stratagy_name]["total"]["holdings_stats"]["last_bar_datetime"]) > stats["portfolio"]["total"]["holdings_stats"]["last_bar_datetime"] \
            else  stats["portfolio"]["total"]["holdings_stats"]["last_bar_datetime"]
        
        stats["portfolio"]["total"]["holdings_stats"]["duration"] = stats["portfolio"]["total"]["holdings_stats"]["last_bar_datetime"] - stats["portfolio"]["total"]["holdings_stats"]["start_date"] 

def calculate_return(stats: dict) -> dict:
    stats["total"]["koefs"]["APR"] = (stats['total']["deals_stats"]["deals_return"] \
                                        / (metrics.get_duration / datetime.timedelta(minutes=1))) \
                                        * (datetime.timedelta(days= 365) / datetime.timedelta(minutes=1))
    stats["total"]["koefs"]["APR"] = float('{:.7f}'.format(stats["total"]["koefs"]["APR"]))
    return stats

def calculate_portfolio_return(stats: dict) -> dict:
    stats = stats.get_stats
    stats["portfolio"]["total"]["koefs"]["APR"] = (stats["portfolio"]['total']["deals_stats"]["deals_return"] \
                                        / (stats["portfolio"]["total"]["holdings_stats"]["duration"] / datetime.timedelta(minutes=1))) \
                                        * (datetime.timedelta(days= 365) / datetime.timedelta(minutes=1))
    stats["portfolio"]["total"]["koefs"]["APR"] = float('{:.5f}'.format(stats["portfolio"]["total"]["koefs"]["APR"]))

def get_equity_curve(all_holdings: dict) -> dict:
    dates = [i["datetime"] for i in all_holdings ]
    capital = [i["total"]["capital"] for i in all_holdings]
    pnl = [i["total"]["pnl"] for i in all_holdings]
    curve = pd.DataFrame({'capital': capital, 'pnl': pnl, 'datetime': dates}).dropna().set_index('datetime')
    curve["returns"] = curve["capital"].pct_change().fillna(0)
    return curve

def calculate_drawdowns(stats: dict, curve: pd.DataFrame):
    capital = curve["capital"].to_list()
    dates = curve.index.to_list()
    dates = [date.to_pydatetime() for date in dates]
    hwm = [0] * len(capital)

    drawdown_pct = [0] * len(capital)
    duration_pct = {0: 0}
    cnt_pct = 0

    drawdown_pcr = [0] * len(capital)
    duration_pcr = {0: 0}
    cnt_pcr = 0

    for i in range(len(capital)):
        hwm[i] = (max(hwm[i - 1], capital[i]))

        drawdown_pct[i] = hwm[i] - capital[i]
        if drawdown_pct[i] == 0:
            cnt_pct = 0
        else:
            cnt_pct += 1
        duration_pct[dates[i]] = cnt_pct

        drawdown_pcr[i] = drawdown_pct[i] / hwm[i]
        if drawdown_pcr[i] == 0:
            cnt_pcr = 0
        else:
            cnt_pcr += 1        
        duration_pcr[dates[i]] = cnt_pcr

    duration_pct_end_date = max(duration_pct, key= duration_pct.get)
    for i in duration_pct:
        if  duration_pct[i] == 0:
            duration_pct_start_date = i
        elif i == duration_pct_end_date:
            break
    
    duration_pcr_end_date = max(duration_pcr, key= duration_pcr.get)
    for i in duration_pcr:
        if  duration_pcr[i] == 0:
            duration_pcr_start_date = i
        elif i == duration_pcr_end_date:
            break

    stats["total"]["koefs"]["DD_pct"] = max(drawdown_pct)
    stats["total"]["koefs"]["DD_pct_date"] =  f'{dates[drawdown_pct.index(max(drawdown_pct))]:%Y-%m-%d %H:%M:%S}'
    if  duration_pct_end_date:
        stats["total"]["koefs"]["DD_pct_duration"] = str(duration_pct_end_date - duration_pct_start_date).split(',')[0]
    else:
        stats["total"]["koefs"]["DD_pct_duration"] = 0

    stats["total"]["koefs"]["DD_pcr"] = max(drawdown_pcr)
    stats["total"]["koefs"]["DD_pcr"] = float('{:.5f}'.format(stats["total"]["koefs"]["DD_pcr"]))
    stats["total"]["koefs"]["DD_pcr_date"] = f'{dates[drawdown_pcr.index(max(drawdown_pcr))]:%Y-%m-%d %H:%M:%S}'
    if duration_pcr_end_date:
        stats["total"]["koefs"]["DD_pcr_duration"] = str(duration_pcr_end_date - duration_pcr_start_date).split(',')[0]
    else:
        stats["total"]["koefs"]["DD_pcr_duration"] = 0

    curve["drawdown_pct"] = drawdown_pct
    curve["drawdown_pcr"] = drawdown_pcr
    return stats, curve

def get_portfolio_equity_curve(curve: dict) -> dict:
    comb_index = pd.core.indexes.datetimes.DatetimeIndex

    for item in curve:
        if comb_index.empty:
            comb_index = curve[item].index
        else:
            comb_index = comb_index.union(curve[item].index)

    for item in curve:
        capital_curve = pd.Series(data= curve[item]["capital"])
        capital_curve = capital_curve.reindex(index= comb_index, method= "pad")
        capital_curve = capital_curve.fillna(item.get_stratagy_params["initial_capital"] * item.get_stratagy_params["stratagy_weight"])

        pnl_curve = pd.Series(data= curve[item]["pnl"])
        pnl_curve = pnl_curve.reindex(index= comb_index, method= None)
        pnl_curve = pnl_curve.fillna(0)

        returns_curve = pd.Series(data= curve[item]["returns"])
        returns_curve = returns_curve.reindex(index= comb_index, method= None)
        returns_curve = returns_curve.fillna(0)

        curve[item] = curve[item].reindex(index= comb_index, method= None)
        curve[item]["capital"] = capital_curve
        curve[item]["pnl"] = pnl_curve
        curve[item]["returns"] = returns_curve

    portfolio_curve = pd.DataFrame(data= 0, index= comb_index, columns= ["capital", "pnl", "returns"])
    for item in curve:
        portfolio_curve["capital"] += curve[item]["capital"]
        portfolio_curve["pnl"] += curve[item]["pnl"]
        portfolio_curve["returns"] += curve[item]["returns"]

    curve["portfolio"] = portfolio_curve
    return curve

def calculate_portfolio_drawdown(stats: dict, curve: dict) -> dict:
    stats = stats.get_stats
    capital = curve["portfolio"]["capital"].to_list()
    dates = curve["portfolio"].index.to_list()

    hwm = [0] * len(capital)

    drawdown_pct = [0] * len(capital)
    duration_pct = {0: 0}
    cnt_pct = 0

    drawdown_pcr = [0] * len(capital)
    duration_pcr = {0: 0}
    cnt_pcr = 0

    for i in range(len(capital)):
        hwm[i] = (max(hwm[i - 1], capital[i]))

        drawdown_pct[i] = hwm[i] - capital[i]
        if drawdown_pct[i] == 0:
            cnt_pct = 0
        else:
            cnt_pct += 1
        duration_pct[dates[i]] = cnt_pct

        drawdown_pcr[i] = drawdown_pct[i] / hwm[i]
        if drawdown_pcr[i] == 0:
            cnt_pcr = 0
        else:
            cnt_pcr += 1        
        duration_pcr[dates[i]] = cnt_pcr

    duration_pct_end_date = max(duration_pct, key= duration_pct.get)
    for i in duration_pct:
        if  duration_pct[i] == 0:
            duration_pct_start_date = i
        elif i == duration_pct_end_date:
            break
    
    duration_pcr_end_date = max(duration_pcr, key= duration_pcr.get)
    for i in duration_pcr:
        if  duration_pcr[i] == 0:
            duration_pcr_start_date = i
        elif i == duration_pcr_end_date:
            break

    stats["portfolio"]["total"]["koefs"]["DD_pct"] = max(drawdown_pct)
    stats["portfolio"]["total"]["koefs"]["DD_pct"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["DD_pct"]))
    stats["portfolio"]["total"]["koefs"]["DD_pct_date"] =  dates[drawdown_pct.index(max(drawdown_pct))]
    if  duration_pct_end_date:
        stats["portfolio"]["total"]["koefs"]["DD_pct_duration"] = convert_str_toDateTime(duration_pct_end_date) - convert_str_toDateTime(duration_pct_start_date)
    else:
        stats["portfolio"]["total"]["koefs"]["DD_pct_duration"] = 0

    stats["portfolio"]["total"]["koefs"]["DD_pcr"] = max(drawdown_pcr)
    stats["portfolio"]["total"]["koefs"]["DD_pcr"] = float('{:.5f}'.format(stats["portfolio"]["total"]["koefs"]["DD_pcr"]))
    stats["portfolio"]["total"]["koefs"]["DD_pcr_date"] = dates[drawdown_pcr.index(max(drawdown_pcr))]
    if duration_pcr_end_date:
        stats["portfolio"]["total"]["koefs"]["DD_pcr_duration"] = convert_str_toDateTime(duration_pcr_end_date) - convert_str_toDateTime(duration_pcr_start_date)
    else:
        stats["portfolio"]["total"]["koefs"]["DD_pcr_duration"] = 0

    curve["portfolio"]["drawdown_pct"] = drawdown_pct
    curve["portfolio"]["drawdown_pcr"] = drawdown_pcr

    return curve

def calculate_apr_to_dd_factor(stats: dict) -> dict:
    if stats["total"]["koefs"]["DD_pcr"]:
        stats["total"]["koefs"]["APR/DD_factor"] = stats["total"]["koefs"]["APR"] / stats["total"]["koefs"]["DD_pcr"] 
        stats["total"]["koefs"]["APR/DD_factor"] = float('{:.3f}'.format(stats["total"]["koefs"]["APR/DD_factor"]))
    else:
        stats["total"]["koefs"]["APR/DD_factor"] = 0
    return stats

def calculate_portfolio_apr_to_dd_factor(stats: dict) -> dict:
    stats = stats.get_stats
    if stats["portfolio"]["total"]["koefs"]["DD_pcr"]:
        stats["portfolio"]["total"]["koefs"]["APR/DD_factor"] = stats["portfolio"]["total"]["koefs"]["APR"] / stats["portfolio"]["total"]["koefs"]["DD_pcr"] 
        stats["portfolio"]["total"]["koefs"]["APR/DD_factor"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["APR/DD_factor"]))
    else:
        stats["portfolio"]["total"]["koefs"]["APR/DD_factor"] = 0

def calculate_recovery_factor(stats: dict) -> dict:
    if stats["total"]["koefs"]["DD_pct"]:
        stats["total"]["koefs"]["recovery_factor"] = stats["total"]["holdings_stats"]["pnl"] / stats["total"]["koefs"]["DD_pct"]
        stats["total"]["koefs"]["recovery_factor"] = float('{:.3f}'.format(stats["total"]["koefs"]["recovery_factor"]))
    else:
        stats["total"]["koefs"]["recovery_factor"] = 0
    return stats

def calculate_portfolio_recovery_factor(stats: dict) -> dict:
    stats = stats.get_stats
    if stats["portfolio"]["total"]["koefs"]["DD_pct"]:
        stats["portfolio"]["total"]["koefs"]["recovery_factor"] = stats["portfolio"]["total"]["holdings_stats"]["pnl"] / stats["portfolio"]["total"]["koefs"]["DD_pct"]
        stats["portfolio"]["total"]["koefs"]["recovery_factor"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["recovery_factor"]))
    else:
        stats["portfolio"]["total"]["koefs"]["recovery_factor"] = 0

def calculate_sharp_ratio(stats: dict, curve: pd.DataFrame) -> dict:
    returns = curve["returns"].to_list()
    std_returns = np.std(returns)
    periods = 252

    if std_returns:
        stats["total"]["koefs"]["sharp_ratio"] = np.sqrt(periods) * (np.mean(returns) / std_returns)
        stats["total"]["koefs"]["sharp_ratio"] = float('{:.3f}'.format(stats["total"]["koefs"]["sharp_ratio"]))
    else:
        stats["total"]["koefs"]["sharp_ratio"] = 0
    return stats

def calculate_portfolio_sharp_ratio(stats: dict, curve: pd.DataFrame) -> dict:
    stats = stats.get_stats
    returns = curve["portfolio"]["returns"].to_list()
    std_returns = np.std(returns)
    periods = 252

    if std_returns:
        stats["portfolio"]["total"]["koefs"]["sharp_ratio"] = np.sqrt(periods) * (np.mean(returns) / std_returns)
        stats["portfolio"]["total"]["koefs"]["sharp_ratio"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["sharp_ratio"]))
    else:
        stats["portfolio"]["total"]["koefs"]["sharp_ratio"] = 0

def calculate_sortino_ratio(stats: dict, curve: pd.DataFrame) -> dict:
    returns = curve["returns"].to_list()
    downside_returns = [i for i in returns if i <= 0]
    std_returns = np.std(downside_returns)

    periods = 252
    if std_returns:
        stats["total"]["koefs"]["sortino_ratio"] = np.sqrt(periods) * (np.mean(returns)) / std_returns
        stats["total"]["koefs"]["sortino_ratio"] = float('{:.3f}'.format(stats["total"]["koefs"]["sortino_ratio"]))
    else:
        stats["total"]["koefs"]["sortino_ratio"] = 0
    return stats

def calculate_portfolio_sortino_ratio(stats: dict, curve: pd.DataFrame) -> dict:
    stats = stats.get_stats
    returns = curve["portfolio"]["returns"].to_list()
    downside_returns = [i for i in returns if i <= 0]
    std_returns = np.std(downside_returns)

    periods = 252
    if std_returns:
        stats["portfolio"]["total"]["koefs"]["sortino_ratio"] = np.sqrt(periods) * (np.mean(returns)) / std_returns
        stats["portfolio"]["total"]["koefs"]["sortino_ratio"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["sortino_ratio"]))
    else:
        stats["portfolio"]["total"]["koefs"]["sortino_ratio"] = 0

def calculate_var(stats: dict, curve: pd.DataFrame, period, quantile, forward) -> dict:
    capital = curve["capital"].to_list()[-(period + 1):]
    returns = curve["returns"].to_list()[-(period + 1):]
    returns = pd.Series(returns)
    log_returns = np.log(1 + returns)
    var = log_returns.quantile(quantile) * capital[-1]
    stats["total"]["koefs"]["var"] = var * np.sqrt(forward)
    stats["total"]["koefs"]["var"] = float('{:.3f}'.format(stats["total"]["koefs"]["var"]))
    return stats

def calculate_portfolio_var(stats: dict, curve: pd.DataFrame, period, quantile, forward) -> dict:
    stats = stats.get_stats
    capital = curve["portfolio"]["capital"].to_list()[-(period + 1):]
    returns = curve["portfolio"]["returns"].to_list()[-(period + 1):]
    returns = pd.Series(returns)
    log_returns = np.log(1 + returns)
    var = log_returns.quantile(quantile) * capital[-1]
    stats["portfolio"]["total"]["koefs"]["var"] = var * np.sqrt(forward)
    stats["portfolio"]["total"]["koefs"]["var"] = float('{:.3f}'.format(stats["portfolio"]["total"]["koefs"]["var"]))
