#!/usr/bin/python
# -*- coding: utf-8 -*-

from handler import instruments_info

def forts_commission(symbol, price) -> float:
    ''' 
    действуют до 19:00 мск 01 апреля 2025 г. включительно. 
    '''

    commission_plan_exchange_futures = {
        "currency": 0.002655,
        "interest_rate": 0.009486,
        "stock": 0.011385,
        "index": 0.003795,
        "commodities": 0.007590
    }

    commission_plan_clearing_futures = {
        "currency": 0.000885,
        "interest_rate": 0.003162,
        "stock": 0.003795,
        "index": 0.001265,
        "commodities": 0.002530
    }

    exchange_rate = commission_plan_exchange_futures[instruments_info[symbol]["commission_type"]] / 100
    exchange_commission = round(round(abs(price) * round(instruments_info[symbol]["step_price"] / instruments_info[symbol]["step"], 5), 2) * exchange_rate, 2)

    clearing_rate = commission_plan_clearing_futures[instruments_info[symbol]["commission_type"]] / 100
    clearing_commission = round(round(abs(price) * round(instruments_info[symbol]["step_price"] / instruments_info[symbol]["step"], 5), 2) * clearing_rate, 2)

    full_commission = exchange_commission + clearing_commission
    return round(full_commission, 2)
