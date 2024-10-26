#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
from commission_plans import forts_commission

def mpr(symbol, capital, mpr, entry_price, exit_price):
    full_commission = forts_commission(symbol, entry_price) + forts_commission(symbol, exit_price)
    return math.floor((capital * (mpr / 100)) / (abs(exit_price - entry_price) + full_commission))
