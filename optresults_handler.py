#!/usr/bin/python
# -*- coding: utf-8 -*-

import argparse, yaml, math, os
import matplotlib.pyplot as plt
import numpy as np

'''
Handler of optimization results.

mode "visual" plot results of optimization by "result_scope".
mode "select" selects parameters which fit to requirements of "result_scope".
'''

def args_parser():
    parser = argparse.ArgumentParser(description="Flags of Command-Line options")
    parser.add_argument(
        "-f", "--file",                                      # указывающий путь к папке с данными
        default= '',                                         # Значение по умолчанию
        required= True,                                      # Необязательный параметр
        type= str,                                           # Тип строковый
        help= "Path to folder with data"
    )
    parser.add_argument(
        "-x", "--xaxis",                                 
        default= '',                                         # Значение по умолчанию
        required= True,                                      # Необязательный параметр
        type= str,                                           # Тип строковый
        help= "Parameter to obtain"
    )
    parser.add_argument(
        "-y", "--yaxis",                                 
        default= '',                                         # Значение по умолчанию
        required= True,                                      # Необязательный параметр
        type= str,                                           # Тип строковый
        help= "Parameter to obtain"
    )
    parser.add_argument(
        "-d", "--dimension",                                 
        default= '',                                         # Значение по умолчанию
        required= True,                                      # Необязательный параметр
        type= str,                                           # Тип строковый
        choices= ["2D", "3D"],
        help= "Dimension of axsis"
    )
    parser.add_argument(
        "-m", "--mode",                                 
        default= '',                                         # Значение по умолчанию
        required= True,                                      # Необязательный параметр
        type= str,                                           # Тип строковый
        choices= ["visual", "select"],
        help= "The mode of handler. Visual = plot graphs. Select = selection of results by mask."
    )
    return parser.parse_args()

def get_yaxis(dict_from_string):
    if args.yaxis in dict_from_string["stratagy_params"]:
        return dict_from_string["stratagy_params"][args.yaxis]
    elif args.yaxis in dict_from_string["stratagy_posSizer_params"]:
        return dict_from_string["stratagy_posSizer_params"][args.yaxis]
    elif args.yaxis in dict_from_string["stratagy_stats"]["total"]["koefs"]:
        return dict_from_string["stratagy_stats"]["total"]["koefs"][args.yaxis]
    elif args.yaxis in dict_from_string["stratagy_stats"]["total"]["deals_stats"]:
        return dict_from_string["stratagy_stats"]["total"]["deals_stats"][args.yaxis]
    elif args.yaxis in dict_from_string["stratagy_stats"]["total"]["holdings_stats"]:
        return dict_from_string["stratagy_stats"]["total"]["holdings_stats"][args.yaxis]

def two_dimensions(args) -> None:
    with open(args.file) as fin:
        lines = fin.readlines()

    results_dict = {}
    for line in lines:
        try:
            line = line.split("; ")
            dict_from_string = yaml.load(line[1], Loader=yaml.Loader)
            if args.xaxis in dict_from_string["stratagy_params"]:
                results_dict[dict_from_string["stratagy_params"][args.xaxis]] = get_yaxis(dict_from_string)
            elif args.xaxis in dict_from_string["stratagy_posSizer_params"]:
                results_dict[dict_from_string["stratagy_posSizer_params"][args.xaxis]] = get_yaxis(dict_from_string)
            elif args.xaxis in dict_from_string["stratagy_stats"]["total"]["koefs"]:
                results_dict[dict_from_string["stratagy_stats"]["total"]["koefs"][args.xaxis]] = get_yaxis(dict_from_string)
            elif args.xaxis in dict_from_string["stratagy_stats"]["total"]["deals_stats"]:
                results_dict[dict_from_string["stratagy_stats"]["total"]["deals_stats"][args.xaxis]] = get_yaxis(dict_from_string)
            elif args.xaxis in dict_from_string["stratagy_stats"]["total"]["holdings_stats"]:
                results_dict[dict_from_string["stratagy_stats"]["total"]["holdings_stats"][args.xaxis]] = get_yaxis(dict_from_string)
        except:
            pass
    
    sorted_result_dict = sorted(results_dict.items())

    x, y = zip(*sorted_result_dict)
    plt.plot(x, y)
    plt.xlabel(args.xaxis)
    plt.ylabel(args.yaxis)
    plt.grid(True)
    plt.show()

def three_dimensions(args) -> None:
    pass

results_scope = {
    "APR/DD_factor": {"value": 4, "optim": "max"},
    "DD_pcr": {"value": 0.25, "optim": "min"},
    "recovery_factor":  {"value": 5, "optim": "max"},
    "profit_factor": {"value": 2, "optim": "max"},
    "expected_payoff_probability": {"value": 0, "optim": "max"},
    "breakeven_tradeoff": {"value": 0, "optim": "max"},
    "sharp_ratio": {"value": 0.1, "optim": "max"},
    "APR": {"value": 0, "optim": "max"},
    "deals_count": {"value": 12, "optim": "max"},
}

def selection_handler(value, stats) -> int:
    if stats["optim"] == "max":
        return 1 if value >= float(stats["value"]) else 0
    elif stats["optim"] == "min":
        return 1 if value <= float(stats["value"]) else 0
    return 0

def selection() -> None:
    file_out = "opt_results/select/select.csv"
    try:
        os.remove(file_out)
    except OSError:
        pass
    with open(args.file, "+r") as fin:
        lines = fin.readlines()
    
    for line in lines:
        try:
            new_line = line.split("; ")
            dict_from_string = yaml.load(new_line[1], Loader= yaml.Loader)
            dict_from_string_keys = dict_from_string["stratagy_stats"]["total"].keys()
            total = 0
            for key in dict_from_string_keys:
                for result in results_scope.keys():
                    if result in dict_from_string["stratagy_stats"]["total"][key]:
                        value = "{:.5f}".format(float(dict_from_string["stratagy_stats"]["total"][key][result]))
                        total += selection_handler(float(value), results_scope[result])
            if total == len(results_scope):
                with open(file_out, "a+") as fout:
                    fout.write(line)
        except:
            pass
    try:
        open(file_out) 
    except:
        print("There is no acceptable results!")

def plot_set_get_yaxis(dict_from_string, results_scope) -> list:
    results_for_key = {key: None for key in results_scope.keys()}
    for key in results_scope.keys():
        if key in dict_from_string["stratagy_params"]:
            results_for_key[key] = dict_from_string["stratagy_params"][key]
        elif key in dict_from_string["stratagy_posSizer_params"]:
            results_for_key[key] = dict_from_string["stratagy_posSizer_params"][key]
        elif key in dict_from_string["stratagy_stats"]["total"]["koefs"]:
            results_for_key[key] = dict_from_string["stratagy_stats"]["total"]["koefs"][key]
        elif key in dict_from_string["stratagy_stats"]["total"]["deals_stats"]:
            results_for_key[key] = dict_from_string["stratagy_stats"]["total"]["deals_stats"][key]
        elif key in dict_from_string["stratagy_stats"]["total"]["holdings_stats"]:
            results_for_key[key] = dict_from_string["stratagy_stats"]["total"]["holdings_stats"][key]
    return results_for_key

def plot_set_get_xaxis(args) -> None:
    with open(args.file) as fin:
        lines = fin.readlines()

    results_dict = {}
    for line in lines:
        line = line.split("; ")
        try:
            dict_from_string = yaml.load(line[1], Loader=yaml.Loader)
            if args.xaxis in dict_from_string["stratagy_params"]:
                results_dict[dict_from_string["stratagy_params"][args.xaxis]] = plot_set_get_yaxis(dict_from_string, results_scope)
            elif args.xaxis in dict_from_string["stratagy_posSizer_params"]:
                results_dict[dict_from_string["stratagy_posSizer_params"][args.xaxis]] = plot_set_get_yaxis(dict_from_string, results_scope)
            elif args.xaxis in dict_from_string["stratagy_stats"]["total"]["koefs"]:
                results_dict[dict_from_string["stratagy_stats"]["total"]["koefs"][args.xaxis]] = plot_set_get_yaxis(dict_from_string, results_scope)
            elif args.xaxis in dict_from_string["stratagy_stats"]["total"]["deals_stats"]:
                results_dict[dict_from_string["stratagy_stats"]["total"]["deals_stats"][args.xaxis]] = plot_set_get_yaxis(dict_from_string, results_scope)
            elif args.xaxis in dict_from_string["stratagy_stats"]["total"]["holdings_stats"]:
                results_dict[dict_from_string["stratagy_stats"]["total"]["holdings_stats"][args.xaxis]] = plot_set_get_yaxis(dict_from_string, results_scope)
        except:
            pass
    return results_dict

def plot_set(args, results_scope) -> None:
    results_dict = plot_set_get_xaxis(args)
    x = sorted(results_dict.keys())
    subplots_cell = math.ceil(np.sqrt(len(results_scope.keys())))
    
    plt.figure("Otimization Results", figsize=(14, 8))
    plt.subplots_adjust(
        hspace= 0.3,
        top= 0.95,
        bottom= 0.05,
        left= 0.05,
        right= 0.95,
        wspace= 0.15)

    for n, key in enumerate(results_scope.keys()):
        ax = plt.subplot(subplots_cell, subplots_cell, n + 1)
        y = [results_dict[item][key] for item in results_dict]
        ax.plot(x, y)
        ax.set_title(key, fontsize=10)
        ax.set_xlabel("")
        ax.grid(True)
    plt.show()

if __name__ == "__main__":
    args = args_parser()
    if args.mode == "visual":
        if args.dimension == "2D":
            if args.yaxis == "set":
                plot_set(args, results_scope)
            else:
                two_dimensions(args)
        elif args.dimension == "3D":
            three_dimensions(args)
    elif args.mode == "select":
        selection()
