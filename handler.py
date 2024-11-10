#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse
import os, datetime

def args_parser():
    parser = argparse.ArgumentParser(description="Flags of Command-Line options")
    parser.add_argument(
        "-sm", "--stats_mode",
        default= "min",
        required= True,
        type= str,
        choices= ["min", "full"],
        help= "min - minimal set of stratagy stats, full - max set of stratagy stats"
    )
    parser.add_argument(
        "-m", "--mode",
        default= "optimyze",
        required= True,
        type= str,
        choices= ["optimize", "visual"],
        help= "optimyze - optimization mode, visual - draw pnl< drawdown etc"
    )
    return parser.parse_args()

def clear_files() -> None:
    file = "opt.csv"
    if os.path.exists(file):
        os.remove(file)

def resample_handler(*params) -> list:
    out = []
    if params[0]["open"] > 0:
        out.append(("open", "first"))
    if params[0]["high"] > 0:
        out.append(("high", "max"))
    if params[0]["low"] > 0:
        out.append(("low", "min"))
    if params[0]["close"] > 0:
        out.append(("close", "last"))
    if params[0]["vol"] > 0:
        out.append(("vol", "sum"))
    if params[0]["oi"] > 0:
        out.append(("oi", "sum"))
    return out

instruments_info = {
    "Si-3.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": "2020-03-19 10:00:00",
        "marginal_costs": 0
    },
    "Si-6.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": "2020-06-18 10:00:00",
        "marginal_costs": 0
    },
    "Si-12.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": 18062020,
        "marginal_costs": 0
    },
    "Si-9.20.txt": {
        "type": "futures",
        "margin": 10_000.00,
        "commission": 3.00,
        "commission_type": "FORTS",
        "expiration_date": 18062020,
        "marginal_costs": 0
    },
    "Si-9.21.txt": {
        "type": "futures",
        "margin": 4_417.03,
        "commission_type": "currency",
        "trade_from_date": "2021-06-17 07:00:00",
        "expiration_date": "2021-09-16 07:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-12.21.txt": {
        "type": "futures",
        "margin": 4_445.25,
        "commission_type": "currency",
        "trade_from_date": "2021-09-16 07:00:00",
        "expiration_date": "2021-12-16 07:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-3.22.txt": {
        "type": "futures",
        "margin": 16_585.75,
        "commission_type": "currency",
        "trade_from_date": "2021-12-16 07:00:00",
        "expiration_date": "2022-03-17 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-6.22.txt": {
        "type": "futures",
        "margin": 5_912.63,
        "commission_type": "currency",
        "trade_from_date": "2022-03-17 10:00:00",
        "expiration_date": "2022-06-16 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-9.22.txt": {
        "type": "futures",
        "margin": 9_136.5,
        "commission_type": "currency",
        "trade_from_date": "2022-06-16 10:00:00",
        "expiration_date": "2022-09-15 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-12.22.txt": {
        "type": "futures",
        "margin": 10_018.69,
        "commission_type": "currency",
        "trade_from_date": "2022-09-15 09:00:00",
        "expiration_date": "2022-12-15 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-3.23.txt": {
        "type": "futures",
        "margin": 12_003.13,
        "commission_type": "currency",
        "trade_from_date": "2022-12-15 09:00:00",
        "expiration_date": "2023-03-16 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-6.23.txt": {
        "type": "futures",
        "margin": 12_583.69,
        "commission_type": "currency",
        "trade_from_date": "2023-03-16 09:00:00",
        "expiration_date": "2023-06-15 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-9.23.txt": {
        "type": "futures",
        "margin": 14_595.32,
        "commission_type": "currency",
        "trade_from_date": "2023-06-15 09:00:00",
        "expiration_date": "2023-09-21 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-12.23.txt": {
        "type": "futures",
        "margin": 13_965.5,
        "commission_type": "currency",
        "trade_from_date": "2023-09-21 09:00:00",
        "expiration_date": "2023-12-21 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-3.24.txt": {
        "type": "futures",
        "margin": 13_861.25,
        "commission_type": "currency",
        "trade_from_date": "2023-12-21 09:00:00",
        "expiration_date": "2024-03-21 09:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-6.24.txt": {
        "type": "futures",
        "margin": 12_394.43,
        "commission_type": "currency",
        "trade_from_date": "2024-03-21 09:00:00",
        "expiration_date": "2024-06-20 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
    "Si-9.24.txt": {
        "type": "futures",
        "margin": 13_750.68,
        "commission_type": "currency",
        "trade_from_date": "2024-06-20 10:00:00",
        "expiration_date": "2024-09-19 10:00:00",
        "marginal_costs": 0,
        "step": 1,
        "step_price": 1
    },
}

def convert_str_toDateTime(string_dateTime: str) -> datetime.datetime:
    format_ = "%Y-%m-%d %H:%M:%S"
    converted_dateTime = datetime.datetime.strptime(string_dateTime, format_)
    return converted_dateTime

def stratagy_name_creator(stratagy_params: dict) -> list:
    params_list = "_".join(str(v[0]) for v in stratagy_params["strat_params"].values())   
    stratagy_name = f'{stratagy_params["stratagy"].__name__}_'    + \
                    f'{stratagy_params["args"]["compression"]}'   + \
                    f'{stratagy_params["args"]["timeframe"]}_'    + \
                    f'{stratagy_params["symbol_base_name"]}_'     + \
                    f'{params_list}_'                             + \
                    f'{stratagy_params["pos_sizer"]["pos_sizer_type"][0]}'
    return stratagy_name

def CustomCSVDataHandlerPortfolio_params_creator(*stratagies) -> None:
    params = {
        stratagy.get_stratagy_params["stratagy_name"]: {
            "folder": stratagy.get_stratagy_params["folder"],
            "data_parser_params": stratagy.get_stratagy_params["data_parser_params"],
            "timeframe": stratagy.get_stratagy_params["timeframe"],
            "compression": stratagy.get_stratagy_params["compression"],
            "symbol_list": stratagy.get_stratagy_params["symbol_list"]
        }
        for stratagy in stratagies
    }
    return params

def create_stats_structe(stratagy_portfolio) -> dict:
    stratagy_names = [stratagy.get_stratagy_params["stratagy_name"] for stratagy in stratagy_portfolio]
    stats_mode = stratagy_portfolio[0].get_stratagy_params["args"]["args"].stats_mode
    
    symbol_list = [stratagy.get_stratagy_params["symbol_list"] for stratagy in stratagy_portfolio]
    symbol_list = [symbol for list_ in symbol_list for symbol in list_]
    symbol_list = list(set(symbol_list))
    
    stats = {}
    stats["curve"] = {stratagy_name: {"capital": 0, "pnl": 0, "datetime": 0} for stratagy_name in stratagy_names}
    stats["curve"]["portfolio"] = {"capital": 0, "pnl": 0, "datetime": 0}
    
    stats["portfolio"] = {stratagy_name: {} for stratagy_name in stratagy_names}
    stats["portfolio"]["total"] = {"koefs": {}, "deals_stats": {}, "holdings_stats": {}}
    stats["portfolio"]["total"]["deals_stats"]["deals_count"] = 0
    stats["portfolio"]["total"]["deals_stats"]["deals_gross_pnl"] = 0
    stats["portfolio"]["total"]["deals_stats"]["commission"] = 0
    stats["portfolio"]["total"]["deals_stats"]["deals_pnl"] = 0

    stats["portfolio"]["total"]["deals_stats"]["win_deals_count"] = 0
    stats["portfolio"]["total"]["deals_stats"]["win_deals_gross_pnl"] = 0
    stats["portfolio"]["total"]["deals_stats"]["win_commission"] = 0
    stats["portfolio"]["total"]["deals_stats"]["win_deals_pnl"] = 0

    stats["portfolio"]["total"]["deals_stats"]["loss_deals_count"] = 0
    stats["portfolio"]["total"]["deals_stats"]["loss_deals_gross_pnl"] = 0
    stats["portfolio"]["total"]["deals_stats"]["loss_commission"] = 0
    stats["portfolio"]["total"]["deals_stats"]["loss_deals_pnl"] = 0

    stats["portfolio"]["total"]["holdings_stats"]["gross_pnl"] = 0
    stats["portfolio"]["total"]["holdings_stats"]["commission"] = 0
    stats["portfolio"]["total"]["holdings_stats"]["pnl"] = 0
    if stats_mode == "full":
        stats["portfolio"]["total"]["holdings_stats"]["long_gross_pnl"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["long_commission"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["long_pnl"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["short_gross_pnl"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["short_commission"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["short_pnl"] = 0
        stats["portfolio"]["total"]["holdings_stats"]["start_date"] = datetime.datetime.now()

    for symbol in symbol_list:
        stats["portfolio"][symbol] = {}
        if stats_mode == "full":
            stats["portfolio"][symbol]["koefs"] = {}
        stats["portfolio"][symbol]["deals_stats"] = {}
        stats["portfolio"][symbol]["deals_stats"]["deals_count"] = 0
        stats["portfolio"][symbol]["deals_stats"]["deals_gross_pnl"] = 0
        stats["portfolio"][symbol]["deals_stats"]["commission"] = 0
        stats["portfolio"][symbol]["deals_stats"]["deals_pnl"] = 0

        stats["portfolio"][symbol]["deals_stats"]["win_deals_count"] = 0
        stats["portfolio"][symbol]["deals_stats"]["win_deals_gross_pnl"] = 0
        stats["portfolio"][symbol]["deals_stats"]["win_commission"] = 0
        stats["portfolio"][symbol]["deals_stats"]["win_deals_pnl"] = 0

        stats["portfolio"][symbol]["deals_stats"]["loss_deals_count"] = 0
        stats["portfolio"][symbol]["deals_stats"]["loss_deals_gross_pnl"] = 0
        stats["portfolio"][symbol]["deals_stats"]["loss_commission"] = 0
        stats["portfolio"][symbol]["deals_stats"]["loss_deals_pnl"] = 0

        stats["portfolio"][symbol]["holdings_stats"] = {}
        stats["portfolio"][symbol]["holdings_stats"]["gross_pnl"] = 0
        stats["portfolio"][symbol]["holdings_stats"]["commission"] = 0
        stats["portfolio"][symbol]["holdings_stats"]["pnl"] = 0

        if stats_mode == "full":
            stats["portfolio"][symbol]["holdings_stats"]["long_gross_pnl"] = 0
            stats["portfolio"][symbol]["holdings_stats"]["long_commission"] = 0
            stats["portfolio"][symbol]["holdings_stats"]["long_pnl"] = 0

            stats["portfolio"][symbol]["holdings_stats"]["short_gross_pnl"] = 0
            stats["portfolio"][symbol]["holdings_stats"]["short_commission"] = 0
            stats["portfolio"][symbol]["holdings_stats"]["short_pnl"] = 0

    return stats
