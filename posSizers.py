#!/usr/bin/python
# -*- coding: utf-8 -*-

import math

def mpr(capital, mpr, entry_price, exit_price, commision):
    return math.floor((capital * (mpr / 100)) / (abs(exit_price - entry_price) + commision * 2))
