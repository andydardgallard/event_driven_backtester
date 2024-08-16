#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime as dt
from commission_plans import forts_commision

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

class MarginCallEvent(Event):
    def __init__(self, symbol: str, datetime: dt, commission=None) -> None:
        super().__init__()
        self.set_event_type = "MARGINCALL"
        self.__symbol = symbol
        self.__datetime = datetime
        self.__commission = commission

        if commission is None:
            self.forts_commision_()
        else:
            self.__commission = commission

    @property
    def get_commission(self) -> float:
        return self.__commission
    
    @get_commission.setter
    def set_commission(self, commission: float) -> None:
        self.__commission = commission

    def forts_commision_(self) -> float:
        self.set_commission = forts_commision()
        return self.__commission
    
    @property
    def get_symbol(self) -> str:
        return self.__symbol

    @property
    def get_datetime(self) -> dt.datetime:
        return self.__datetime

class SignalEvent(Event):
    def __init__(self, stratagy_id: int, symbol: str, datetime: dt, signal_params: dict, commission=None) -> None:
        super().__init__()
        self.set_event_type = "SIGNAL"
        self.__stratagy_id = stratagy_id
        self.__symbol = symbol
        self.__datetime = datetime
        self.__signal_params = signal_params
        self.__commission = commission

        if commission is None:
            self.forts_commision_()
        else:
            self.__commission = commission

    @property
    def get_commission(self) -> float:
        return self.__commission
    
    @get_commission.setter
    def set_commission(self, commission: float) -> None:
        self.__commission = commission

    def forts_commision_(self) -> float:
        self.set_commission = forts_commision()
        return self.__commission
    
    @property
    def get_signal_params(self) -> dict:
        return self.__signal_params

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
    def get_signal_name(self) -> str:
        return self.get_signal_params["signal_name"]

class OrderEvent(Event):
    def __init__(self, symbol, order_type, quantity, direction, signal_params, timeindx) -> None:
        super().__init__()
        self.set_event_type = "ORDER"
        self.__symbol = symbol
        self.__order_type = order_type
        self.__quantity = quantity
        self.__direction = direction
        self.__timeindx = timeindx
        self.__signal_params = signal_params

    
    @property
    def get_signal_params(self) -> dict:
        return self.__signal_params
    
    @property
    def get_signal_name(self) -> str:
        return self.get_signal_params["signal_name"]
    
    @property
    def get_pos_sizer(self) -> str:
        return self.__pos_sizer

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
        print(f"Oredr: symbol= {self.get_symbol}, type= {self.get_order_type}, quantity= {self.get_quantity}, direction= {self.get_direction}, timeindx= {self.get_timeindx}")

class FillEvent(Event):
    def __init__(self, timeindx, symbol, exchange, quantity, direction, signal_params, fill_cost, commission=None) -> None:
        super().__init__()
        self.set_event_type = "FILL"
        self.__timeindx = timeindx
        self.__symbol = symbol
        self.__exchange = exchange
        self.__quantity = quantity
        self.__direction = direction
        self.__fill_cost = fill_cost
        self.__commission = commission
        self.__signal_params = signal_params
        
        if commission is None:
            self.forts_commision_()
        else:
            self.__commission = commission
            

    @property
    def get_signal_params(self) -> dict:
        return self.__signal_params

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

    def forts_commision_(self) -> float:
        self.set_commission = forts_commision()
        return self.__commission
