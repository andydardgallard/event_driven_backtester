#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import datetime as dt
from queue import Queue
from event import Event, OrderEvent, FillEvent

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
                # dt.datetime.utcnow(),
                event.get_timeindx,
                event.get_symbol,
                "FORTS",
                event.get_quantity,
                event.get_direction,
                None
            )
        self.__events.put(fill_event)
