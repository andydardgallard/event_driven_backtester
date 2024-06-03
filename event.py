#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime as dt
import queue

class Event(object):
    def __init__(self) -> None:
        super().__init__()
        self.__type = None
    
    @property
    def get_event_type(self) -> str:
        return self.__type
    
    @get_event_type.setter
    def set_event_type(self, type: str) -> None:
        self.__type = type

class MarketEvent(Event):
    def __init__(self) -> None:
        super().__init__()
        self.set_event_type = "MARKET"

class SignalEvent(Event):
    def __init__(self, stratagy_id, symbol, datetime, signal_type, strength) -> None:
        super().__init__()
        self.set_event_type = "SIGNAL"
        self.__stratagy_id = stratagy_id
        self.__symbol = symbol
        self.__datetime = datetime
        self.__signal_type = signal_type
        self.__strength = strength

    @property
    def get_stratagy_id(self) -> str:
        return self.__stratagy_id

    @property
    def get_symbol(self) -> str:
        return self.__symbol

    @property
    def get_datetime(self) -> dt.datetime:
        return self.__datetime

    @property
    def get_signal_type(self) -> str:
        return self.__signal_type

    @property
    def get_strength(self) -> str:
        return self.__strength

class OrderEvent(Event):
    def __init__(self, symbol, order_type, quantity, direction, timeindx) -> None:
        super().__init__()
        self.set_event_type = "ORDER"
        self.__symbol = symbol
        self.__order_type = order_type
        self.__quantity = quantity
        self.__direction = direction
        self.__timeindx = timeindx

    @property
    def get_symbol(self) -> str:
        return self.__symbol

    @property
    def get_order_type(self) -> str:
        return self.__order_type

    @property
    def get_quantity(self) -> str:
        return self.__quantity

    @property
    def get_direction(self) -> int:
        return self.__direction

    @property
    def get_timeindx(self) -> None:
        return self.__timeindx

    def print_order(self) -> None:
        print(f"Oredr: symbol= {self.get_symbol}, type= {self.get_order_type}, quantity= {self.get_quantity}, direction= {self.get_direction}")

class FillEvent(Event):
    def __init__(self, timeindx, symbol, exchange, quantity, direction, fill_cost, commission=None) -> None:
        super().__init__()
        self.set_event_type = "FILL"
        self.__timeindx = timeindx
        self.__symbol = symbol
        self.__exchange = exchange
        self.__quantity = quantity
        self.__direction = direction
        self.__fill_cost = fill_cost
        self.__commission = commission
        

        if commission is None:
            self.__commission  = 0.0
        else:
            self.forts_commision()

    @property
    def get_timeindx(self) -> dt.datetime:
        return self.__timeindx

    @property
    def get_symbol(self) -> str:
        return self.__symbol

    @property
    def get_exchange(self) -> str:
        return self.__exchange

    @property
    def get_quantity(self) -> int:
        return self.__quantity

    @property
    def get_direction(self) -> int:
        return self.__direction

    @property
    def get_fill_cost(self) -> float:
        return self.__fill_cost

    @property
    def get_commission(self) -> float:
        return self.__commission

    @get_commission.setter
    def set_commission(self, commission: float) -> None:
        self.__commission = commission

    def forts_commision(self) -> float:
        #TODO commission module
        self.set_commission = 3.14
        return self.__commission
