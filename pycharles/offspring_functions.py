import random
from functools import partial
from pycharles.binary_utils import *


def slice_and_stitch(subject1, subject2, values):
    bits1 = seq_to_binary_string(subject1, values)
    bits2 = seq_to_binary_string(subject2, values)
    max_length = len(bits1)
    r = random.randint(0, max_length)
    new_bits1 = bits1[0:r] + bits2[r:max_length]
    new_bits2 = bits2[0:r] + bits1[r:max_length]
    return binary_string_to_seq(new_bits1,values), binary_string_to_seq(new_bits2,values)


def slice_and_stitch_func(values):
    return partial(slice_and_stitch, values=values)


def parents_similarity(subject1, subject2, values):
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
    return partial(parents_similarity, values=values)