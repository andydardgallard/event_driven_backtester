#!/usr/bin/python
# -*- coding: utf-8 -*-

from pprint import pprint
from event import Event
from handler import instruments_info

def marginCall_control(current_holdings: dict, quantity: int, margin_params: dict, event: Event):
    if event.get_event_type == "SIGNAL":
        symbol = event.get_symbol
        if event.get_signal_params["signal_name"][symbol] != "EXIT":
            capital = current_holdings["total"]["capital"]
            if instruments_info[symbol]["type"] == "futures":
                initial_margin = quantity * instruments_info[symbol]["margin"]
                if capital > initial_margin:
                    return 1
                else:
                    print(f'Not enough initial margin {initial_margin} to entry {symbol} #{quantity} = {capital}!')
                    return 0
    elif event.get_event_type == "MARKET":
        if current_holdings["total"]["cash"] < 0:
            capital = 0
            for symbol in list(quantity.keys())[:-1]:
                if instruments_info[symbol]["type"] == "futures":
                    if quantity[symbol]["position"] != 0:
                        capital += quantity[symbol]["entryCapital"]
            min_margin = capital * margin_params["min_margin"]
            if current_holdings["total"]["capital"] > min_margin:
                return 1
            else:
                print(f'Not enough minimal margin {min_margin} with {current_holdings["total"]["capital"]} of cash!')
                return 0
        else:
            return 1
