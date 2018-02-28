import random
from functools import partial
from pycharles.binary_utils import *


def slice_and_stitch(subject1, subject2, values):
    """
    This function creates new subjects by taking the two subjects provided, transform then to a binary encoding
    and then randomly selecting a position where they will be sliced. The new subjects are made of the first part
    of one subject and the second part of the second subject. As an example, assume the binary encoding of the two
    subjects are s1 = '000000' and s2 = '111111', and assume the random position was chosen right in the middle.
    The two new subjects will be s1_new = '000111' and s2_new = '111000'.

    :param subject1: one subject of the population
    :param subject2: another subject of the population
    :param values: list or dict. a sequence of all values a subject in the population can have
    :return: a tuple of two new subjects
    """
    bits1 = seq_to_binary_string(subject1, values)
    bits2 = seq_to_binary_string(subject2, values)
    max_length = len(bits1)
    r = random.randint(0, max_length)
    new_bits1 = bits1[0:r] + bits2[r:max_length]
    new_bits2 = bits2[0:r] + bits1[r:max_length]
    return binary_string_to_seq(new_bits1,values), binary_string_to_seq(new_bits2,values)


def slice_and_stitch_func(values):
    """
    This function creates a partial function of slice_and_stitch to be used by the model.

    :param values: list or dict. a sequence of all values a subject in the population can have
    :return: a partial function f(subject1, subject2) => (new_subject1, new_subject2)
    """
    return partial(slice_and_stitch, values=values)


def parents_similarity(subject1, subject2, values):
    """
    This function creates two new subjects by comparing the bits of the binary encoded provided subjects (the
    parents). If both parents have the same bit in a certain location, the offspring have a very high probability
    of having the same bit too in that location. If the parents' bits are opposite, than the offspring's bits
    are chosen randomly. For example, say the parents are s1 = '11000' and s2 = '11101', then with high probability
    the offspring will be s1_new = '11100' and s2_new = '11001' (the middle and last digit are randomly chosen).

    :param subject1: one subject of the population
    :param subject2: another subject of the population
    :param values: list or dict. a sequence of all values a subject in the population can have
    :return: a tuple of two new subjects
    """
    def create_child(bits1, bits2):
        child = ''
        for i in range(0,len(bits1)):
            r = random.random()
            if bits1[i] == bits2[i]:
                take_from_1 = r < 0.9
            else:
                take_from_1 = r < 0.5
            if take_from_1:
                new_bit = bits1[i]
            else:
                new_bit = bits2[i]
            child += new_bit
        return child
    bits1 = seq_to_binary_string(subject1, values)
    bits2 = seq_to_binary_string(subject2, values)
    new_bits1 = create_child(bits1, bits2)
    new_bits2 = create_child(bits2, bits1)
    return binary_string_to_seq(new_bits1, values), binary_string_to_seq(new_bits2, values)


def parents_similarity_func(values):
    """
    This function creates a partial function of parents_similarity to be used by the model.

    :param values: list or dict. a sequence of all values a subject in the population can have
    :return: a partial function f(subject1, subject2) => (new_subject1, new_subject2)
    """
    return partial(parents_similarity, values=values)