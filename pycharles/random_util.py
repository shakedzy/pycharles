import random


def positive_random():
    """
    Generated a random float number in the range (0,1] rather than [0,1).
    :return: a random number
    """
    r = random.random()
    if r == 0.0:
        r = 1.0
    return r
