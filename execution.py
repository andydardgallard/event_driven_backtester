#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from queue import Queue
from event import OrderEvent, FillEvent, MarginCallEvent

class ExecutionHandler(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute_order(self, event: OrderEvent):
        raise NotImplementedError("Should implement execute_order()")

class SimulatedExecutionHandler(ExecutionHandler):
    def __init__(self, events: Queue) -> None:
        super().__init__()
        self.__events = events
    
    @property
    def get_events(self) -> Queue:
        return self.__events

    def execute_order(self, event: OrderEvent):
        if event.get_event_type == "ORDER":
            fill_event = FillEvent(
                event.get_timeindx,
                event.get_symbol,
                "FORTS",
                event.get_quantity,
                event.get_direction,
                event.get_signal_params,
                fill_cost= 0.0,
                commission= None
            )
        self.__events.put(fill_event)

    def execute_margin_call(self, event: MarginCallEvent) -> None:
        if event.get_event_type == "MARGINCALL":
            pass
            #TODO marginCall_executor
