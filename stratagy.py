#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
import datetime
import queue
import numpy as np
import pandas as pd
from event import SignalEvent

class Stratagy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")