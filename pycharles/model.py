import time
import math
import random
from pycharles import random_util
from pycharles.element import Element


class Model:
    _default_end_reason = (-1, None)
    _default_duplication_replace_attempts = 3

    _all_values = list()
    _initial_population = list()
    _strength_function = None
    _offspring_function = None
    _elitism_ratio = None
    _mutations_odds = None
    _generations = None
    _duplication_policy = None
    _seed = None
    _elements = list()
    _end_reason = _default_end_reason
    _current_generation = 0
    _duplication_replace_attempts = _default_duplication_replace_attempts
    _verbose = False

    def __init__(self, population, all_values, strength_function, offspring_function,
                 elitism_ratio=0.1, mutation_odds=0.001, generations=10,
                 duplication_policy='ignore', seed=int(time.time()), verbose=False):
        self._all_values = all_values
        self._initial_population = population
        self.set_strength_function(strength_function)
        self.set_offspring_function(offspring_function)
        self.set_elitism_ratio(elitism_ratio)
        self.set_mutation_odds(mutation_odds)
        self.set_generations(generations)
        self.set_duplication_policy(duplication_policy)
        self.set_seed(seed)
        self.set_verbosity(verbose)
        self._set_population(population)

    def set_strength_function(self, strength_function): self._strength_function = strength_function
    def set_offspring_function(self, offspring_function): self._offspring_function = offspring_function
    def set_verbosity(self, verbose): self._verbose = verbose

    def set_duplication_policy(self, duplication_policy):
        dp = duplication_policy.lower()
        if dp == 'ignore' or dp == 'kill' or dp == 'replace':
            self._duplication_policy = dp
            self._duplication_replace_attempts = self._default_duplication_replace_attempts
        elif dp.startswith('replace:'):
            att = dp.split(':')[1]
            if att < 1:
                raise ValueError("Invalid number of attempts")
            else:
                self._duplication_replace_attempts = att
        else:
            raise ValueError("Invalid duplication policy")

    def set_elitism_ratio(self, elitism_ratio):
        if elitism_ratio < 0.0 or elitism_ratio > 1.0:
            raise ValueError("Elitism ratio must be a number in the range [0,1]")
        else:
            self._elitism_ratio = elitism_ratio

    def set_mutation_odds(self, mutation_odds):
        if mutation_odds < 0.0 or mutation_odds > 1.0:
            raise ValueError("Mutations odds must be a number in the range [0,1]")
        else:
            self._mutations_odds = mutation_odds

    def set_generations(self, generations):
        if generations > 0:
            self._generations = generations
        else:
            raise ValueError("Generations number must be a non-negative integer")

    def set_seed(self, seed):
        self._seed = seed
        random.seed(seed)

    def _set_population(self, population):
        if all(len(subject) == len(population[0]) for subject in population):
            self._elements = list(map(lambda subject: Element(subject),population))
        else:
            raise ValueError("All subjects in the population must have the same size")

    def get_strength_function(self): return self._strength_function
    def get_elitism_ratio(self): return self._elitism_ratio
    def get_mutation_odds(self): return self._mutations_odds
    def get_generations(self): return self._generations
    def get_seed(self): return self._seed
    def get_elements(self): return self._elements
    def get_population(self): return list(map(lambda el: el.get_genes(), self._elements))
    def get_offspring_function(self): return self._offspring_function
    def get_end_reason(self): return self._end_reason
    def get_current_generation(self): return self._current_generation
    def get_duplication_policy(self):
        if self._duplication_policy == 'replace':
            return 'replace:{}'.format(self._duplication_replace_attempts)
        else:
            return self._duplication_policy

    def _kill_misfits(self): self._elements = [el for el in self._elements if el.get_strength() > 0.0]

    def _print(self, text):
        if self._verbose:
            print(text)

    def _select_element(self, ignore_this_element=None):
        if ignore_this_element is None:
            p = 0.0
        else:
            p = ignore_this_element.get_probability()
        r = random_util.positive_random() * (1.0 - p)
        prob_sum = 0.0
        selected = None
        for element in self._elements:
            if ignore_this_element is None or ignore_this_element != element:
                p = element.get_probability()
                if prob_sum + p >= r:
                    selected = element
                else:
                    prob_sum += p
        if selected is None:
            selected = self._elements[-1]
        return selected

    def reset(self):
        self._set_population(self._initial_population)
        self._end_reason = self._default_end_reason
        self._current_generation = 0

    def get_best(self,n=1):
        if n == 1:
            return self._elements[0].get_genes()
        else:
            [el.get_genes() for el in self._elements[0:n]]

    def _handle_duplicates(self):
        if self._duplication_policy == 'kill':
            self._elements = list(set(self._elements))
        elif self._duplication_policy == 'replace':
            for _ in range(0,self._duplication_replace_attempts):
                n = len(self._elements)
                self._elements = list(set(self._elements))
                missing = n - len(self._elements)
                if missing == 0:
                    break
                else:
                    number_of_couples = math.ceil(missing/2)
                    new_elements = self._breed(number_of_couples)
                    if missing % 2 > 0:
                        del new_elements[0]
                    self._elements += new_elements
        else:
            pass

    def _breed(self, number_of_couples):
        elements = list()
        for _ in range(0,number_of_couples):
            father = self._select_element()
            mother = self._select_element(ignore_this_element=father)
            child1genes, child2genes = self._offspring_function(father.get_genes(),mother.get_genes())
            elements.append(Element(child1genes))
            elements.append(Element(child2genes))
        return elements

    def evolve(self):
        self._end_reason = self._default_end_reason
        for g in range(0,self._generations+1):
            self._print('Evolving - current generation: {0}, population size: {1}'.format(g,len(self._elements)))
            self._current_generation = g
            if g > 0:
                el_num = len(self._elements)
                self._kill_misfits()
                if len(self._elements) < 2:
                    self._end_reason = (2, 'Population perished')
                    break
                elitism_num = round(self._elitism_ratio * el_num)
                elitists = self._elements[0:elitism_num]
                remaining_couples_num = math.floor((el_num-elitism_num)/2)
                self._elements = elitists + self._breed(remaining_couples_num)
                self._handle_duplicates()
                for el in self._elements:
                    el.mutate(self._mutations_odds,self._all_values)
            for el in self._elements:
                el.set_strength(self._strength_function)
            total_strength = sum([el.get_strength() for el in self._elements])
            for el in self._elements:
                el.strength_to_probability(total_strength)
            self._elements.sort(reverse=True)
            if any(math.isinf(el.get_strength()) for el in self._elements):
                self._end_reason = (1, 'Ideal solution found')
                break
        if self._end_reason == self._default_end_reason:
            self._end_reason = (0, 'Evolution completed')
        self._print('Evolution stopped: cause: {0} [reason ID: {1}]'
                    .format(self.get_end_reason()[1],self.get_end_reason()[0]))
