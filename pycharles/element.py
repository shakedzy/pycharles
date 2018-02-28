import math
import random
from pycharles.binary_utils import *


class Element:
    """
    An Element is a single subject extension in the overall population. I consists of several genes.
    An Element has a strength which is derived from a certain predefined Strength Function (sometimes
    refer to as Fitness Function). The higher an element's strength is, the higher are hus chance of
    reproducing and survival. An Element can also mutate, which is the act of a spontaneous change of
    one of its genes.
    """

    _genes = list()
    _strength = 0.0
    _probability = 0.0

    def __init__(self, genes):
        """
        create a new Element
        :param genes: The genes of the new Element
        """
        self.set_genes(genes)

    def get_strength(self): return self._strength
    def get_probability(self): return self._probability
    def get_genes(self): return self._genes

    def set_genes(self, genes): self._genes = genes

    def set_strength(self, strength_function):
        """
        Calculates the strength of the Element usng the provided strength_function.

        :param strength_function: a function that maps a sequence of values to a non-negative number
        """
        s = strength_function(self._genes)
        if s < 0.0:
            raise ValueError("Strength must be non-negative")
        else:
            self._strength = s
            self._probability = 0.0

    def strength_to_probability(self, total_strength):
        """
        Compute the Element's survival-probability, which is basically its normalized strength over the entire
        population's combined strength

        :param total_strength: the entire's population's combined strength
        """
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
        """
        Mutate the Element. Behind the scenes, all genes are converted to binary representations, and for each binary
        bit, there's a probability it will suddenly flip and change its value. After this process, the binary
        representation is transformed back to the new genes.

        :param mutation_odds: a number in the continuous range [0,1], representing the probability of a bit flipping
                              its value
        :param values: list or dict. a sequence of all values a subject in the population can have
        """
        new_genes = list()
        for i,g in enumerate(self._genes):
            if isinstance(values, dict):
                gene = values[i].index(g)
            else:
                gene = values.index(g)
            bits = int_to_binary_string(gene)
            gene_size = get_single_gene_bits_num(values,i)
            padded_bits = pad_binary_string(bits,gene_size)
            mutated_bits = ''
            for b in padded_bits:
                r = random.random()
                if r <= mutation_odds:
                    b = flip_bit_char(b)
                mutated_bits += b
            new_genes.append(get_value_of_binary_string(mutated_bits, values, i))
        self.set_genes(new_genes)

    # The hash, eq, ne functions are used to compare elements based on their genes.
    def __hash__(self):
        return hash(''.join(map(lambda x: str(x), self._genes)))

    def __eq__(self, other):
        return self.__hash__() == hash(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    # The lt, le, gt, ge functions are used to compare elements based on their strength. This is use for sorting.
    def __lt__(self, other):
        return self._strength < other.get_strength()

    def __le__(self, other):
        return self._strength <= other.get_strength()

    def __gt__(self, other):
        return not self.__lt__(other)

    def __ge__(self, other):
        return not self.__le__(other)