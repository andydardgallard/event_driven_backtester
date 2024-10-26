#!/usr/bin/python
# -*- coding: utf-8 -*-

from concurrent.futures import ProcessPoolExecutor
from backtest import Backtest
from data import CustomCSVDataExecutor as dExec
from execution import SimulatedExecutionHandler
from portfolio import Portfolio
from itertools import product
from abc import ABCMeta, abstractmethod
import random, yaml, time
import numpy as np
import matplotlib.pyplot as plt

class Optimizer(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self) -> None:
        pass
        
    @abstractmethod
    def __call__(self, opt_params) -> None:
        self.__opt_params = opt_params
    
    @property
    @abstractmethod
    def get_opt_params(self) -> dict:
        return self.__opt_params

    @property
    @abstractmethod
    def get_fitness(self):
        return self._fitness

    @abstractmethod
    def _fitness(*params_list):
        backtest = Backtest(
            params_list,
            dExec,
            SimulatedExecutionHandler,
            Portfolio
        )
        if params_list[1]["args"].mode == "optimize":
            return backtest.simulate_trading_opt()
        elif params_list[1]["args"].mode == "visual":
            return backtest.simulate_trading_visual()

class Grid_Search(Optimizer):
    '''
    Optimization search of all parameters
    '''

    def __init__(self) -> None:
        super().__init__()

    @property
    def get_params_creator(self):
        return self.optimization_params_handler

    def __call__(self, opt_params, params_creator, workers):
        super().__call__(opt_params)
        params_list = params_creator()
        with ProcessPoolExecutor(max_workers= workers) as executor:
            results = (executor.map(self.get_fitness, params_list))
        return results

    def optimization_params_handler(self) -> list:
        indicators_params = [self.get_opt_params["strat_params"][key] for key in self.get_opt_params["strat_params"]]
        pos_sizer_params = [self.get_opt_params["pos_sizer"][key] for key in self.get_opt_params["pos_sizer"]]
        product_ = list(product(*indicators_params, *pos_sizer_params))
        params_list = []
        i = 1
        
        for item in product_:
            params_dict = {}
            params_dict["indicators"] = {key: item[indx] for indx, key in enumerate(self.get_opt_params["strat_params"])}
            params_dict["pos_sizers"] = {key: item[indx + len(self.get_opt_params["strat_params"])] for indx, key in enumerate(self.get_opt_params["pos_sizer"])}
            params_dict["data_iter"] = self.get_opt_params["data_iter"]
            params_dict["args"] = self.get_opt_params["args"]
            params_dict["item_number"] = i
            params_dict["length"] = len(product_)
            params_dict["stratagy"] = self.get_opt_params["stratagy"]
            params_dict["initial_capital"] = self.get_opt_params["initial_capital"]
            params_dict["margin_params"] = self.get_opt_params["margin_params"]
            i += 1
            params_list.append(params_dict)
        return params_list
    
class Genetic_Search(Optimizer):
    '''
    Optimization of parameters search by genetic algorithm
    '''
    
    def __init__(self) -> None:
        super().__init__()
        self.__nmbr_of_generation = 0
        self.__nmbr_of_individ = 1

    @property
    def get_plot_data(self):
        return self.__plot_data

    @property
    def get_ga_stats(self) -> dict:
        return self.__ga_stats

    @property
    def get_number_of_individ(self) -> int:
        return self.__nmbr_of_individ
    
    @get_number_of_individ.setter
    def set_number_of_individ(self, nmbr: int) -> None:
        self.__nmbr_of_individ = nmbr
    
    @property
    def get_populations(self) -> list:
        return self.__populations
    
    @property
    def get_nmbr_of_generation(self) -> int:
        return self.__nmbr_of_generation
    
    @get_nmbr_of_generation.setter
    def set_nmbr_of_generation(self, nmbr: int) -> None:
         self.__nmbr_of_generation = nmbr

    @property
    def get_ga_params(self) -> dict:
        return self.__ga_params

    @property
    def get_tournament_winners(self) -> dict:
        return self.__tournamet_winners
    
    @property
    def get_hromosome_bank(self) -> list:
        return self.__hromosome_bank
    
    @get_hromosome_bank.setter
    def set_hromosome_bank(self, hromosome: dict) -> None:
        self.__hromosome_bank.append(hromosome)

    def __call__(self, opt_params, ga_params, workers, plot= False) -> None:
        super().__call__(opt_params)
        self.__ga_params = ga_params
        self.set_data_storage = self.get_opt_params["data_iter"]
        self.__populations = self.construct_populations()
        self.__ga_stats = self.constrauct_ga_stats()
        self.__tournamet_winners = self.construct_populations()
        self.__hromosome_bank = []
        self.__plot_data = {
            "number_of_generation": [],
            "best_individ": [],
            "mean": [],
            "best_hromosome_ID": []
        }

        population_optimizer = Grid_Search()
        start_time = time.time()
        print(f'Generation # {self.get_nmbr_of_generation}')
        results = population_optimizer(opt_params, self.create_initial_population, workers= workers)
        for result in results:
            self._parse_results(result)
        self.calculate_generation_stats()
        self._tournament_selection()
        end_time = time.time()
        print(f"Elapsed_time for Generation# {self.get_nmbr_of_generation} = {end_time - start_time}")
        
        while self.get_nmbr_of_generation < self.get_ga_params["max_generations"]:
            start_time = time.time()
            self.set_nmbr_of_generation += 1
            print(f'Generation # {self.get_nmbr_of_generation}')

            results = population_optimizer(opt_params, self._crossover_mutation, workers= workers)
            for result in results:
                self._parse_results(result)
            self.calculate_generation_stats()
            self._tournament_selection()
            end_time = time.time()
            print(f"Elapsed_time for Generation# {self.get_nmbr_of_generation} = {end_time - start_time}")
        
        if plot == True:
            self._plot_results()

    def construct_populations(self) -> dict:
        g = dict((key, value) for key, value in [(generation, {}) for generation in range(self.get_ga_params["max_generations"] + 1)])
        for gen in g:
            g[gen] = dict((key, value) for key, value in [(nmbr_of_individ, {}) for nmbr_of_individ in range(1, self.get_ga_params["population_size"] + 1)])
            for individ in range(1, self.get_ga_params["population_size"] + 1):
                g[gen][individ]["indicators"] = None
                g[gen][individ]["pos_sizers"] = None
                g[gen][individ]["data_iter"] = self.get_opt_params["data_iter"]
                g[gen][individ]["args"] = self.get_opt_params["args"]
                g[gen][individ]["item_number"] = 0
                g[gen][individ]["length"] = self.get_ga_params["population_size"]
                g[gen][individ]["stratagy"] = self.get_opt_params["stratagy"]
                g[gen][individ]["initial_capital"] = self.get_opt_params["initial_capital"]
                g[gen][individ]["margin_params"] = self.get_opt_params["margin_params"]
                g[gen][individ]["ga_params"] = {}
                g[gen][individ]["ga_params"]["nmbr_of_generation"] = gen
                g[gen][individ]["ga_params"]["nmbr_of_individ"] = 0
                g[gen][individ]["ga_params"]["fitness"] = self.get_ga_params["fitness_value"]
                g[gen][individ]["ga_params"]["fitness_value"] = None
                g[gen][individ]["ga_params"]["hromosome_ID"] = None
        return g

    def constrauct_ga_stats(self) -> dict:
        d = dict((key, value) for key, value in [(nmbr_of_generation, {}) for nmbr_of_generation in range(self.get_ga_params["max_generations"] + 1)])
        for gen in range(self.get_ga_params["max_generations"] + 1):
            d[gen]["number_of_generation"] = 0
            d[gen]["best_individ"] = 0
            d[gen]["best_hromosome_ID"] = None
            d[gen]["worst_individ"] = 0
            d[gen]["worst_hromosome_ID"] = None
            d[gen]["mean"] = 0
        return d
    
    def create_initial_population(self) -> dict:
        gen = self.get_nmbr_of_generation
        cnt = 1
        while cnt <= self.get_ga_params["population_size"]:
            self.get_populations[gen][cnt]["indicators"] = {key: random.choice(self.get_opt_params["strat_params"][key]) for indx, key in enumerate(self.get_opt_params["strat_params"])}
            self.get_populations[gen][cnt]["pos_sizers"] = {key: random.choice(self.get_opt_params["pos_sizer"][key]) for indx, key in enumerate(self.get_opt_params["pos_sizer"])}
            self.get_populations[gen][cnt]["item_number"] = cnt
            self.get_populations[gen][cnt]["ga_params"]["nmbr_of_individ"] = self.get_number_of_individ
            self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] = self._create_hromosome_ID(self.get_populations[gen][cnt]["indicators"], self.get_populations[gen][cnt]["pos_sizers"])
            self.set_number_of_individ += 1
            if not any(self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] in hromosome for hromosome in self.set_hromosome_bank):
                self.set_hromosome_bank = {self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"]: None}
            cnt += 1

        population = [self.get_populations[gen][cnt] for cnt in self.get_populations[gen]]
        return population

    def _create_hromosome_ID(self, indicators, pos_sizers) -> list:
        individ_id_indicator = [indicators[key] for key in indicators.keys()]
        individ_id_pos_sizers = [pos_sizers[key] for key in pos_sizers.keys()]
        individ_id = individ_id_indicator + individ_id_pos_sizers
        return tuple(individ_id)
    
    def _parse_results(self, result: str) -> None:
        gen = self.get_nmbr_of_generation
        number_of_individ = int(result.split(" ")[1])
        new_line = result.split("; ")
        dict_from_string = yaml.load(new_line[1], Loader= yaml.Loader)

        if self.get_ga_params["fitness_value"] in dict_from_string["stratagy_stats"]["total"]["koefs"]:
            self.get_populations[gen][number_of_individ]["ga_params"]["fitness_value"] = dict_from_string["stratagy_stats"]["total"]["koefs"][self.get_ga_params["fitness_value"]]
        elif self.get_ga_params["fitness_value"] in dict_from_string["stratagy_stats"]["total"]["deals_stats"]:
            self.get_populations[gen][number_of_individ]["ga_params"]["fitness_value"] = dict_from_string["stratagy_stats"]["total"]["deals_stats"][self.get_ga_params["fitness_value"]]
        elif self.get_ga_params["fitness_value"] in dict_from_string["stratagy_stats"]["total"]["holdings_stats"]:
            self.get_populations[gen][number_of_individ]["ga_params"]["fitness_value"] = dict_from_string["stratagy_stats"]["total"]["holdings_stats"][self.get_ga_params["fitness_value"]]
        else:
            print(f"Wrong parameter of fitness_value: {self.get_ga_params['fitness_value']}")
            exit(0)

    def calculate_generation_stats(self):
        gen = self.get_nmbr_of_generation
        self.get_ga_stats[gen]["number_of_generation"] = gen
        values = [self.get_populations[gen][item]["ga_params"]["fitness_value"] for item in range(1, self.get_ga_params["population_size"] + 1)]

        if self.get_ga_params["fitness_direction"] == "max":
            self.get_ga_stats[gen]["best_individ"] = max(values)
            self.get_ga_stats[gen]["worst_individ"] = min(values)
        elif self.get_ga_params["fitness_direction"] == "min":
            self.get_ga_stats[gen]["best_individ"] = min(values)
            self.get_ga_stats[gen]["worst_individ"] = max(values)
        else:
            print(f"Wrong fitness direction - {self.get_ga_params["fitness_direction"]}!")
            exit(0)

        self.get_ga_stats[gen]["mean"] = np.mean(values)
        
        self.get_ga_stats[gen]["best_hromosome_ID"] = [
            self.get_populations[gen][item]["ga_params"]["hromosome_ID"] for 
            item in range(1, self.get_ga_params["population_size"] + 1) if 
            self.get_populations[gen][item]["ga_params"]["fitness_value"] == 
            self.get_ga_stats[gen]["best_individ"]][0]
        
        self.get_ga_stats[gen]["worst_hromosome_ID"] = [
            self.get_populations[gen][item]["ga_params"]["hromosome_ID"] for 
            item in range(1, self.get_ga_params["population_size"] + 1) if 
            self.get_populations[gen][item]["ga_params"]["fitness_value"] == 
            self.get_ga_stats[gen]["worst_individ"]][0]

        print(f'Result of population: Number of generation= {gen}, best= {self.get_ga_stats[gen]["best_individ"]}, mean= {self.get_ga_stats[gen]["mean"]}, worst= {self.get_ga_stats[gen]["worst_individ"]}, best individ ID= {self.get_ga_stats[gen]["best_hromosome_ID"]}')

        self.__plot_data["number_of_generation"].append(self.get_nmbr_of_generation)
        self.__plot_data["best_individ"].append(self.get_ga_stats[gen]["best_individ"])
        self.__plot_data["mean"].append(self.get_ga_stats[gen]["mean"])
        self.__plot_data["best_hromosome_ID"].append(self.get_ga_stats[gen]["best_hromosome_ID"])

        for hromosome in self.get_hromosome_bank:
            for individ in self.get_populations[gen]:
                if self.get_populations[gen][individ]["ga_params"]["hromosome_ID"] == list(hromosome.keys())[0]:
                    hromosome[list(hromosome.keys())[0]] = self.get_populations[gen][individ]["ga_params"]["fitness_value"]
                    break

    def _tournament_selection(self) -> list:
        gen = self.get_nmbr_of_generation
        # best_individ
        first_item_in_new_population = 1
        for individ in self.get_populations[gen]:
            if self.get_populations[gen][individ]["ga_params"]["hromosome_ID"] == self.get_ga_stats[gen]["best_hromosome_ID"]:
                self.get_tournament_winners[gen][first_item_in_new_population]["indicators"] = self.get_populations[gen][individ]["indicators"]
                self.get_tournament_winners[gen][first_item_in_new_population]["pos_sizers"] = self.get_populations[gen][individ]["pos_sizers"]
                self.get_tournament_winners[gen][first_item_in_new_population]["item_number"] = self.get_populations[gen][individ]["item_number"]
                self.get_tournament_winners[gen][first_item_in_new_population]["ga_params"]["nmbr_of_individ"] = self.get_populations[gen][individ]["ga_params"]["nmbr_of_individ"]
                self.get_tournament_winners[gen][first_item_in_new_population]["ga_params"]["fitness_value"] = self.get_populations[gen][individ]["ga_params"]["fitness_value"]
                self.get_tournament_winners[gen][first_item_in_new_population]["ga_params"]["hromosome_ID"] = self.get_populations[gen][individ]["ga_params"]["hromosome_ID"]
                break
        cnt = 2
        while cnt <= self.get_ga_params["population_size"]:
            tournament_room = random.sample(list(self.get_populations[gen].keys()), 2)
            if self.get_ga_params["fitness_direction"] == "max":
                if self.get_populations[gen][tournament_room[0]]["ga_params"]["fitness_value"] > self.get_populations[gen][tournament_room[1]]["ga_params"]["fitness_value"]:
                    wining_individ = {tournament_room[0]: self.get_populations[gen][tournament_room[0]]}
                else:
                    wining_individ = {tournament_room[1]: self.get_populations[gen][tournament_room[1]]}
            elif self.get_ga_params["fitness_direction"] == "min":
                if self.get_populations[gen][tournament_room[0]]["ga_params"]["fitness_value"] < self.get_populations[gen][tournament_room[1]]["ga_params"]["fitness_value"]:
                    wining_individ = {tournament_room[0]: self.get_populations[gen][tournament_room[0]]}
                else:
                    wining_individ = {tournament_room[1]: self.get_populations[gen][tournament_room[1]]}
            else:
                print(f"Wrong fitness direction in tournament - {self.get_ga_params["fitness_direction"]}!")
            
            self.get_tournament_winners[gen][cnt]["indicators"] = wining_individ[list(wining_individ.keys())[0]]["indicators"]
            self.get_tournament_winners[gen][cnt]["pos_sizers"] = wining_individ[list(wining_individ.keys())[0]]["pos_sizers"]
            self.get_tournament_winners[gen][cnt]["item_number"] = wining_individ[list(wining_individ.keys())[0]]["item_number"]
            self.get_tournament_winners[gen][cnt]["ga_params"]["nmbr_of_individ"] = wining_individ[list(wining_individ.keys())[0]]["ga_params"]["nmbr_of_individ"]
            self.get_tournament_winners[gen][cnt]["ga_params"]["fitness_value"] = wining_individ[list(wining_individ.keys())[0]]["ga_params"]["fitness_value"]
            self.get_tournament_winners[gen][cnt]["ga_params"]["hromosome_ID"] = wining_individ[list(wining_individ.keys())[0]]["ga_params"]["hromosome_ID"]
            cnt += 1

    def _crossover_mutation(self) -> list:
        gen = self.get_nmbr_of_generation
        # best_individ
        first_item_in_new_population = 1
        for individ in self.get_tournament_winners[gen - 1]:
            if self.get_tournament_winners[gen - 1][individ]["ga_params"]["hromosome_ID"] == self.get_ga_stats[gen - 1]["best_hromosome_ID"]:
                self.get_populations[gen][individ]["indicators"] = self.get_tournament_winners[gen - 1][first_item_in_new_population]["indicators"]
                self.get_populations[gen][individ]["pos_sizers"] = self.get_tournament_winners[gen - 1][first_item_in_new_population]["pos_sizers"] 
                self.get_populations[gen][individ]["item_number"] = self.get_tournament_winners[gen - 1][first_item_in_new_population]["item_number"]
                self.get_populations[gen][individ]["ga_params"]["nmbr_of_individ"] = self.get_tournament_winners[gen - 1][first_item_in_new_population]["ga_params"]["nmbr_of_individ"]
                self.get_populations[gen][individ]["ga_params"]["fitness_value"] = self.get_tournament_winners[gen - 1][first_item_in_new_population]["ga_params"]["fitness_value"]
                self.get_populations[gen][individ]["ga_params"]["hromosome_ID"] = self.get_tournament_winners[gen - 1][first_item_in_new_population]["ga_params"]["hromosome_ID"]
            break
        cnt = 2
        # crossover
        for child1, child2 in zip(list(self.get_tournament_winners[gen - 1].items())[::2], list(self.get_tournament_winners[gen - 1].items())[1::2]):
            if random.random() < self.get_ga_params["p_crossover"]:
                self.get_populations[gen][cnt]["indicators"] = {key: random.choice([child1[1]["indicators"][key], child2[1]["indicators"][key]]) for indx, key in enumerate(self.get_opt_params["strat_params"])}
                self.get_populations[gen][cnt]["pos_sizers"] = {key: random.choice([child1[1]["pos_sizers"][key], child2[1]["pos_sizers"][key]]) for indx, key in enumerate(self.get_opt_params["pos_sizer"])}
                self.get_populations[gen][cnt]["item_number"] = cnt
                self.get_populations[gen][cnt]["ga_params"]["nmbr_of_individ"] = self.get_number_of_individ
                self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] = self._create_hromosome_ID(self.get_populations[gen][cnt]["indicators"], self.get_populations[gen][cnt]["pos_sizers"])
                if not any(self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] in hromosome for hromosome in self.set_hromosome_bank):
                    self.set_hromosome_bank = {self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"]: None}
                else:
                    fitness_value = [item for item in self.get_hromosome_bank if list(item.keys())[0] == self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"]]
                    self.get_populations[gen][cnt]["ga_params"]["fitness_value"] = list(fitness_value[0].values())[0]
                self.set_number_of_individ += 1
                cnt += 1
        while cnt <= self.get_ga_params["population_size"]:
            # mutation
            if random.random() < self.get_ga_params["p_mutation"]:
                self.get_populations[gen][cnt]["indicators"] = {key: random.choice(self.get_opt_params["strat_params"][key]) for indx, key in enumerate(self.get_opt_params["strat_params"])}
                self.get_populations[gen][cnt]["pos_sizers"] = {key: random.choice(self.get_opt_params["pos_sizer"][key]) for indx, key in enumerate(self.get_opt_params["pos_sizer"])}
                self.get_populations[gen][cnt]["item_number"] = cnt
                self.get_populations[gen][cnt]["ga_params"]["nmbr_of_individ"] = self.get_number_of_individ
                self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] = self._create_hromosome_ID(self.get_populations[gen][cnt]["indicators"], self.get_populations[gen][cnt]["pos_sizers"])
                if not any(self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] in hromosome for hromosome in self.set_hromosome_bank):
                    self.set_hromosome_bank = {self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"]: None}
                else:
                    fitness_value = [item for item in self.get_hromosome_bank if list(item.keys())[0] == self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"]]
                    self.get_populations[gen][cnt]["ga_params"]["fitness_value"] = list(fitness_value[0].values())[0]
                self.set_number_of_individ += 1
            # fill
            else:
                individ = random.choice(list(self.get_tournament_winners[gen - 1].keys()))
                self.get_populations[gen][cnt]["indicators"] = self.get_tournament_winners[gen - 1][individ]["indicators"]
                self.get_populations[gen][cnt]["pos_sizers"] = self.get_tournament_winners[gen - 1][individ]["pos_sizers"]
                self.get_populations[gen][cnt]["item_number"] = cnt
                self.get_populations[gen][cnt]["ga_params"]["nmbr_of_individ"] = self.get_tournament_winners[gen - 1][individ]["ga_params"]["nmbr_of_individ"]
                self.get_populations[gen][cnt]["ga_params"]["fitness_value"] = self.get_tournament_winners[gen - 1][individ]["ga_params"]["fitness_value"]
                self.get_populations[gen][cnt]["ga_params"]["hromosome_ID"] = self.get_tournament_winners[gen - 1][individ]["ga_params"]["hromosome_ID"]
            cnt += 1
        population = [self.get_populations[gen][cnt] for cnt in self.get_populations[gen] if self.get_populations[gen][cnt]["ga_params"]["fitness_value"] == None]
        return population
        
    def _plot_results(self) -> None:
        x = self.__plot_data["number_of_generation"]
        y1 = self.__plot_data["best_individ"]
        y2 = self.__plot_data["mean"]
        plt.plot(x, y1, y2)
        plt.title("Genetic Algorythm")
        plt.xlabel("number_of_generation")
        plt.ylabel("best_individ")
        plt.grid(True)
        plt.text(x[1], y1[1] * 0.9, f'{self.__plot_data["best_hromosome_ID"][-1]}')
        plt.show()
