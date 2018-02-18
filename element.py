import math
import random
from binary_utils import *


class Element:
    _genes = list()
    _strength = 0.0
    _probability = 0.0

    def __init__(self, genes):
        self.set_genes(genes)

    def get_strength(self): return self._strength
    def get_probability(self): return self._probability
    def get_genes(self): return self._genes

    def set_genes(self, genes): self._genes = genes

    def set_strength(self, strength_function):
        s = strength_function(self._genes)
        if s < 0.0:
            raise ValueError("Strength must be non-negative")
        else:
            self._strength = s
            self._probability = 0.0

    def strength_to_probability(self, total_strength):
        if total_strength < 0.0:
            raise ValueError("Combined strength of the entire population cannot be negative")
        else:
            if math.isinf(total_strength):
                if math.isinf(self._strength):
                    self._probability = 1.0
                else:
                    self._probability = 0.0
            else:
                p = self._strength/total_strength
                if p < 0.0 or p > 1.0:
                    raise ValueError("Encountered problematic probability {} for strength {} ad combined strength {}"
                                     .format(p,self._strength,total_strength))
                else:
                    self._probability = p

    def mutate(self, mutation_odds, values):
        gene_size = get_single_gene_bits_num(values)
        new_genes = list()
        for g in self._genes:
            bits = int_to_binary_string(values.index(g))
            padded_bits = pad_binary_string(bits,gene_size)
            mutated_bits = ''
            for b in padded_bits:
                r = random.random()
                if r <= mutation_odds:
                    b = flip_bit_char(b)
                mutated_bits += b
            new_genes.append(get_value_of_binary_string(mutated_bits, values))
        self.set_genes(new_genes)


    def __hash__(self):
        return hash(''.join(self._genes))

    def __eq__(self, other):
        return self.__hash__() == hash(other)

    def __lt__(self, other):
        return self._strength < other.get_strength()

    def __le__(self, other):
        return self._strength <= other.get_strength()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        return not self.__lt__(other)

    def __ge__(self, other):
        return not self.__le__(other)