import time
import math
import random
from pycharles import offspring_functions
from pycharles import random_util
from pycharles.element import Element


class Model:
    """
    A Genetic Model.
    """
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
    _early_stop = None
    _mutate_elitists = False

    def __init__(self, population, all_values, strength_function, offspring_function='slice_and_stitch',
                 elitism_ratio=0.1, mutation_odds=0.001, generations=10,
                 early_stop=None, mutate_elitists=False, duplication_policy='ignore',
                 seed=int(time.time()), verbose=False):
        """
        Model's constructor

        :param population: a sequence of subjects (sometimes refer to as Chromosomes in Genetic Model's terminology),
                           where each subject is a sequence of genes
        :param all_values: list or dict. a sequence of all values a subject in the population can have
        :param strength_function: a function that maps a subject in the population to a non-negative number from 0 to
                                  inf, which represents its strength, and therefore it probability to survive and
                                  reproduce. The higher the number, the stronger the subject is
        :param offspring_function: string or a function of (subject1, subject2) => (new_subject1, new_subject2).
                                   a reproduction function that maps two subjects to two new subjects. This is the
                                   definition of the reproduction mechanism works, and how to create the offspring of
                                   two subjects in the population
        :param elitism_ratio: a continuous number in the range [0,1], representing the percentage of elitists in each
                              generation. Elitists are the strongest subject in their generation, and therefore survive
                              and advance untouched to the next generation
        :param mutation_odds: a continuous number in the range [0,1], which determines the probability for mutation of
                              the subjects in each generation. A mutation is a single binary bit in the subject's genes
                              being randomly flipped (subjects are transformed to binary representation behind the
                              scenes)
        :param generations: a non-negative integer, which determines the number of iterations the model will do
        :param early_stop: None or a positive integer. When not None, The model
                           will stop if a better solution was not found after the amount of generations specified
        :param mutate_elitists: Boolean. Set if elitists can mutate when transferring from one generation to
                                the next one
        :param duplication_policy: string. The policy of the model regarding duplicates in the population at the end of
                                   each generation. See README file for more details.
        :param seed: a seed to be supplied to the model's pseudo-random number generator
        :param verbose: Boolean. Set verbosity level
        """
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
        self.set_early_stop(early_stop)
        self.set_elitists_mutation(mutate_elitists)
        self._set_population(population)

    def set_strength_function(self, strength_function): self._strength_function = strength_function
    def set_verbosity(self, verbose): self._verbose = verbose
    def set_elitists_mutation(self, mutate_elitists): self._mutate_elitists = mutate_elitists

    def set_offspring_function(self, offspring_function):
        if isinstance(offspring_function, str):
            if offspring_function == 'slice_and_stitch':
                self._offspring_function = offspring_functions.slice_and_stitch_func(self._all_values)
            elif offspring_function == 'parents_similarity':
                self._offspring_function = offspring_functions.parents_similarity_func(self._all_values)
            else:
                raise ValueError('Unknown offspring function {0}'.format(offspring_function))
        else:
            self._offspring_function = offspring_function

    def set_early_stop(self, patience):
        if patience is not None:
            if patience == 0:
                patience = None
            elif patience < 0:
                raise ValueError("Early stop patience must be a positive integer or None")
        self._early_stop = patience

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

    def get_population(self): return list(map(lambda el: el.get_genes(), self._elements))
    def get_end_reason(self): return self._end_reason
    def get_current_generation(self): return self._current_generation

    def _kill_misfits(self):
        """
        his function removes all Elements of the population with strength 0, as they have no chance of
        reproduce or survive
        """
        self._elements = [el for el in self._elements if el.get_strength() > 0.0]

    def _print(self, text):
        if self._verbose:
            print(text)

    def _select_element(self, ignore_this_element=None):
        """
        This function randomly selects a single Element of a population based on their strength.
        An ordered population is preferred for performance, where the first Element of the population has
        the highest probability of survival and reproduction, and the rest are ordered by a decreasing
        order of their strength (and survival probability).

        :param ignore_this_element: if defined, this Element will not participate in the random selection
        :return: a random Element of the population
        """
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
        """
        Reset the population to the initial population
        """
        self._set_population(self._initial_population)
        self._end_reason = self._default_end_reason
        self._current_generation = 0

    def get_best(self,n=1):
        """
        Returns the n strongest subject in the population

        :param n: how may subjects to return
        :return: if n==1, return a single subject. if n>1, return a list of subjects, with decreasing strength.
        """
        if n == 1:
            return self._elements[0].get_genes()
        else:
            [el.get_genes() for el in self._elements[0:n]]

    def _handle_duplicates(self):
        """
        This function applies the duplication policy onto the population.
        """
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
        """
        This function is responsible for creating a pair of new Elements based on the number of pairs
        requested. The model's offspringFunction is used for the creation of new Elements.

        :param number_of_couples: the number of pairs of new Elements to create
        :return: a sequence of the new Elements created
        """
        elements = list()
        for _ in range(0,number_of_couples):
            father = self._select_element()
            mother = self._select_element(ignore_this_element=father)
            child1genes, child2genes = self._offspring_function(father.get_genes(),mother.get_genes())
            elements.append(Element(child1genes))
            elements.append(Element(child2genes))
        return elements

    def evolve(self):
        """
        The model's main procedure. This starts the evolution of the subjects of the population
        for the specified amount of generations. This includes reproduction, elitists survival
        and mutation.
        """
        highest_strength = 0
        last_round_updated_highest_strength = 0
        self._end_reason = self._default_end_reason
        for g in range(0,self._generations+1):
            self._print('Evolving - starting generation: {0}, population size: {1}, best solution so far: {2}'
                        .format(g, len(self._elements), self.get_best()))
            self._current_generation = g
            if g > 0:
                el_num = len(self._elements)
                self._kill_misfits()
                if len(self._elements) < 2:
                    self._end_reason = (2, 'Population perished')
                    break
                elitism_num = round(self._elitism_ratio * el_num)
                elitists = self._elements[0:elitism_num]
                remaining_couples_num = round((el_num-elitism_num)/2)
                new_born = self._breed(remaining_couples_num)[0:el_num-elitism_num]
                if self._mutate_elitists:
                    self._elements = elitists + new_born
                    for el in self._elements:
                        el.mutate(self._mutations_odds, self._all_values)
                else:
                    for el in new_born:
                        el.mutate(self._mutations_odds,self._all_values)
                    self._elements = elitists + new_born
                self._handle_duplicates()
            for el in self._elements:
                el.set_strength(self._strength_function)
            total_strength = sum([el.get_strength() for el in self._elements])
            for el in self._elements:
                el.strength_to_probability(total_strength)
            self._elements.sort(reverse=True)
            if math.isinf(self._elements[0].get_strength()):
                self._end_reason = (1, 'Ideal solution found')
                break
            if self._elements[0].get_strength() > highest_strength:
                highest_strength = self._elements[0].get_strength()
                last_round_updated_highest_strength = g
            if self._early_stop is not None:
                if g - last_round_updated_highest_strength >= self._early_stop:
                    self._end_reason = (3, 'Early stop')
                    break
        if self._end_reason == self._default_end_reason:
            self._end_reason = (0, 'Evolution completed')
        self._print('Evolution stopped: cause: {0} [reason ID: {1}]'
                    .format(self.get_end_reason()[1],self.get_end_reason()[0]))
