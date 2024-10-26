#!/usr/bin/python
# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod

class Stratagy(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def calculate_signals(self):
        raise NotImplementedError("Should implement calculate_signals()")