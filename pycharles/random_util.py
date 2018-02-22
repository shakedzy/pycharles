import random


def positive_random():
    r = random.random()
    if r == 0.0:
        r = 1.0
    return r
