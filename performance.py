#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

def create_sharp_ratio(returns, periods= 252):
    return np.sqrt(periods) * (np.mean(returns)) / np.std(returns)

def create_drawdowns(pnl: pd.Series):
    hwm = [0]
    indx = pnl.index
    drawdown = pd.Series(index= indx)
    duration = pd.Series(index= indx)
    for i in range(1, len(indx)):
        hwm.append(max(hwm[i-1], pnl.iloc[i]))
        drawdown.iloc[i] = hwm[i] - pnl.iloc[i]
        duration.iloc[i] = (0 if drawdown.iloc[i] == 0 else duration.iloc[i-1] + 1)
    return drawdown, drawdown.max(), duration.max()
   