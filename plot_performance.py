#!/usr/bin/python
# -*- coding: utf-8 -*-

import os.path, yaml, math
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from pprint import pprint
from handler import convert_str_toDateTime
from stats import stats
from performance import *
import seaborn as sns

def plot_portfolio_pnl_drawdowns(stratagy_portfolio: list, curve: dict) -> None:
    plot_dir = f"{os.getcwd()}/opt_results/visual/temp"
    for stratagy in stratagy_portfolio:
        print(f'Plot curve for {stratagy.get_stratagy_params["stratagy_name"]}')

        with open(f'{plot_dir}/curve_{stratagy.get_stratagy_params["stratagy_name"]}.csv', '+r') as fin:
            data = pd.read_csv(fin, sep= ';', header= 0, index_col= "datetime")

        os.remove(f'{plot_dir}/curve_{stratagy.get_stratagy_params["stratagy_name"]}.csv')

        x = data.index.to_list()
        x = [convert_str_toDateTime(date) for date in x]

        pnl = np.array(data["pnl"].cumsum().to_list())
        returns = data["returns"]
        returns = np.array(returns.apply(lambda x: x * 100).cumsum().to_list())

        drawdown_pct = data["drawdown_pct"].to_list()
        drawdown_pcr = data["drawdown_pcr"]
        drawdown_pcr = np.array(drawdown_pcr.apply(lambda x: x * 100).to_list())

        fig, ax = plt.subplots(2, 2, figsize=(14, 8))
        fig.canvas.manager.set_window_title("Cumulative PnL vs Drawdown_pct")
        fig.suptitle(f'{stratagy.get_stratagy_params["stratagy_name"]}', fontsize= 10)
        plt.subplots_adjust(hspace=0, wspace=0)

        color = 'tab:blue'
        ax[0, 0].plot(x, pnl, color)
        ax[0, 0].set_ylabel('PnL', color=color)
        ax[0, 0].tick_params(axis='y', labelcolor=color)
        ax[0, 0].grid(True)
        ax[0, 0].fill_between(x, pnl, 0, where= (pnl >= 0), interpolate=True, color= color)
        ax[0, 0].fill_between(x, pnl, 0, where= (pnl < 0), interpolate=True, color='red')
        ax[0, 0].set_xticklabels([])

        ax[0, 1].plot(x, returns, color)
        ax[0, 1].set_ylabel('Returns', color= color, rotation= -90, labelpad= 15)
        ax[0, 1].yaxis.set_label_position("right")
        ax[0, 1].yaxis.tick_right()
        ax[0, 1].tick_params(axis='y', labelcolor=color)
        ax[0, 1].grid(True)
        ax[0, 1].fill_between(x, returns, 0, where= (returns >= 0), interpolate=True, color= color)
        ax[0, 1].fill_between(x, returns, 0, where= (returns < 0), interpolate=True, color='red')
        ax[0, 1].set_xticklabels([])

        color = "tab:red"
        ax[1, 0].plot(x, drawdown_pct, color)
        ax[1, 0].set_xlabel('dates')
        ax[1, 0].set_ylabel('Drawdown_pct', color=color)
        ax[1, 0].tick_params(axis='y', labelcolor=color)
        ax[1, 0].fill_between(x, drawdown_pct, color= color)
        ax[1, 0].grid(True)
        for label in ax[1, 0].get_xticklabels():
            label.set_fontsize(9)
            label.set_rotation(-15)

        ax[1, 1].plot(x, drawdown_pcr, color)
        ax[1, 1].set_xlabel('dates')
        ax[1, 1].set_ylabel('Drawdown_prc, %', color= color, rotation= -90, labelpad= 15)
        ax[1, 1].yaxis.set_label_position("right")
        ax[1, 1].yaxis.tick_right()
        ax[1, 1].tick_params(axis= 'y', labelcolor= color)
        ax[1, 1].fill_between(x, drawdown_pcr, color= color)
        ax[1, 1].grid(True)
        for label in ax[1, 1].get_xticklabels():
            label.set_fontsize(9)
            label.set_rotation(-15)

    x = curve["portfolio"].index.to_list()
    x = [convert_str_toDateTime(date) for date in x]

    pnl = np.array(curve["portfolio"]["pnl"].cumsum().to_list())
    returns = curve["portfolio"]["returns"]
    returns = np.array(returns.apply(lambda x: x * 100).cumsum().to_list())

    drawdown_pct = curve["portfolio"]["drawdown_pct"].to_list()
    drawdown_pcr = curve["portfolio"]["drawdown_pcr"]
    drawdown_pcr = np.array(drawdown_pcr.apply(lambda x: x * 100).to_list())

    fig, axp = plt.subplots(2, 2, figsize=(14, 8))
    fig.canvas.manager.set_window_title("Cumulative PnL vs Drawdown_pct")
    fig.suptitle(f'Portfolio', fontsize= 10)
    plt.subplots_adjust(hspace=0, wspace=0)

    color = 'tab:blue'
    axp[0, 0].plot(x, pnl, color)
    for stratagy in stratagy_portfolio:
        pnl_stratagy = np.array(curve[stratagy]["pnl"].cumsum().to_list())
        axp[0, 0].plot(x, pnl_stratagy, lw= 0.5, color= 'black')
    axp[0, 0].set_ylabel('PnL', color=color)
    axp[0, 0].tick_params(axis='y', labelcolor=color)
    axp[0, 0].grid(True)
    axp[0, 0].fill_between(x, pnl, 0, where= (pnl >= 0), interpolate=True, color= color)
    axp[0, 0].fill_between(x, pnl, 0, where= (pnl < 0), interpolate=True, color='red')
    axp[0, 0].set_xticklabels([])

    axp[0, 1].plot(x, returns, color)
    for stratagy in stratagy_portfolio:
        returns_stratagy = curve[stratagy]["returns"]
        returns_stratagy = np.array(returns_stratagy.apply(lambda x: x * 100).cumsum().to_list())
        axp[0, 1].plot(x, returns_stratagy, lw= 0.5, color= 'black')
    axp[0, 1].set_ylabel('Returns', color= color, rotation= -90, labelpad= 15)
    axp[0, 1].yaxis.set_label_position("right")
    axp[0, 1].yaxis.tick_right()
    axp[0, 1].tick_params(axis='y', labelcolor=color)
    axp[0, 1].grid(True)
    axp[0, 1].fill_between(x, returns, 0, where= (returns >= 0), interpolate=True, color= color)
    axp[0, 1].fill_between(x, returns, 0, where= (returns < 0), interpolate=True, color='red')
    axp[0, 1].set_xticklabels([])

    color = "tab:red"
    axp[1, 0].plot(x, drawdown_pct, color)
    axp[1, 0].set_xlabel('dates')
    axp[1, 0].set_ylabel('Drawdown_pct', color=color)
    axp[1, 0].tick_params(axis='y', labelcolor=color)
    axp[1, 0].fill_between(x, drawdown_pct, color= color)
    axp[1, 0].grid(True)
    for label in ax[1, 0].get_xticklabels():
        label.set_fontsize(9)
        label.set_rotation(-15)

    axp[1, 1].plot(x, drawdown_pcr, color)
    axp[1, 1].set_xlabel('dates')
    axp[1, 1].set_ylabel('Drawdown_prc, %', color= color, rotation= -90, labelpad= 15)
    axp[1, 1].yaxis.set_label_position("right")
    axp[1, 1].yaxis.tick_right()
    axp[1, 1].tick_params(axis= 'y', labelcolor= color)
    axp[1, 1].fill_between(x, drawdown_pcr, color= color)
    axp[1, 1].grid(True)
    for label in ax[1, 1].get_xticklabels():
        label.set_fontsize(9)
        label.set_rotation(-15)

    # plot correlation matrix
    matrix = pd.DataFrame()
    for stratagy in curve:
        if type(stratagy).__name__ != "str":
            matrix[type(stratagy).__name__] = curve[stratagy]["capital"].values

    plt.figure("Correletion Matrix", figsize=(14, 8))
    sns.heatmap(matrix.corr(), annot = True, fmt = '.2f')

    os.rmdir(f"{plot_dir}")
    plt.show()

def output_portfolio_performance(stratagy_portfolio: list) -> None:
    stats_portfolio = stats(stratagy_portfolio)
    curve_dir = f"{os.getcwd()}/opt_results/visual/temp"
    curve = {stratagy: 0 for stratagy in stratagy_portfolio}  

    if os.path.exists(curve_dir):
        for stratagy in stratagy_portfolio:
            stats_file = f"{curve_dir}/visual_{stratagy.get_stratagy_params["stratagy_name"]}.csv"
            with open(stats_file, 'r+') as fin:
                line = fin.readlines()
            os.remove(f'{curve_dir}/visual_{stratagy.get_stratagy_params["stratagy_name"]}.csv')

            stats_portfolio.get_stats["portfolio"][stratagy.get_stratagy_params["stratagy_name"]] = yaml.load(line[0], Loader=yaml.Loader)

            get_portfolio_deals_stats(stats_portfolio, stratagy)
            calculate_portfolio_winRate(stats_portfolio, stratagy)
            calculate_portfolio_expected_payoff(stats_portfolio, stratagy)
            calculate_portfolio_breakeven(stats_portfolio, stratagy)
            calculate_portfolio_breakeven_with_tradeoff(stats_portfolio, stratagy, 0.1)
            calculate_portfolio_profit_factor(stats_portfolio, stratagy)
            get_portfolio_holdings_stats(stats_portfolio, stratagy)
            calculate_portfolio_return(stats_portfolio)

            curve_file =  f"{curve_dir}/curve_{stratagy.get_stratagy_params["stratagy_name"]}.csv"
            with open(curve_file, 'r+') as fin:
                curve_data = pd.read_csv(fin, sep= ';', header= 0, index_col= "datetime").sort_index()
            curve[stratagy] = curve_data

        
        curve = get_portfolio_equity_curve(curve)
        curve = calculate_portfolio_drawdown(stats_portfolio, curve)
        calculate_portfolio_apr_to_dd_factor(stats_portfolio)
        calculate_portfolio_recovery_factor(stats_portfolio)
        calculate_portfolio_sharp_ratio(stats_portfolio, curve)
        calculate_portfolio_sortino_ratio(stats_portfolio, curve)
        calculate_portfolio_var(stats_portfolio, curve, 6500, 0.01, 5)
    
    stats_dir = f"{os.getcwd()}/opt_results/visual"
    if not os.path.exists(stats_dir):
        os.makedirs(stats_dir)
    stats_file = f"{stats_dir}/visual_portfolio.csv"
    with open(stats_file, 'w+') as fout:
        pprint(stats_portfolio.get_stats, fout)
    
    return curve

def plot_portfolio_genetic_results(plot_data) -> None:
    subplots_cell = math.ceil(np.sqrt(len(plot_data.keys())))
    
    plt.figure("Genetic Algorythm Results", figsize=(14, 8))
    plt.subplots_adjust(
        hspace= 0.3,
        top= 0.95,
        bottom= 0.05,
        left= 0.05,
        right= 0.95,
        wspace= 0.15)

    for n, key in enumerate(plot_data.keys()):
        ax = plt.subplot(subplots_cell, subplots_cell, n + 1)
        x = plot_data[key]["number_of_generation"]
        y1 = plot_data[key]["best_individ"]
        y2 = plot_data[key]["mean"]
        ax.plot(x, y1, y2)
        ax.set_title(f'{type(key).__name__}: {key.get_stratagy_params["ga_params"]["fitness_value"]}', fontsize= 10)
        ax.text(x[1], y1[1] * 0.9, f'{plot_data[key]["best_hromosome_ID"][-1]}')
        ax.set_xlabel("")
        ax.grid(True)
    plt.show()
