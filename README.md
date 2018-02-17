# PyCharles
A Genetic-Model library in **Python 3.x**. 

This library is based on the original [Charles library in Scala](https://github.com/shakedzy/charles).

![Charles Darwin](https://i.guim.co.uk/img/media/83381c9b4b97c3eefd1c6f67cd32f819e22fab80/60_206_3398_4246/master/3398.jpg?w=300&q=55&auto=format&usm=12&fit=max&s=d3ece4b003774449dc14053a243597a9)

_Charles Darwin, 1809-1882_

### Some reading and examples:
* [Genetic Algorithms on Wikipedia](https://en.wikipedia.org/wiki/Genetic_algorithm)
* This [blog post](https://burakkanber.com/blog/machine-learning-genetic-algorithms-part-1-javascript/) with a simple tutorial and an example

## Usage:
Quick start:
```
from model import Model
model = Model(population, all_values, strength_function, offspring_function)
model.evolve()
solution = model.get_best()
```
Basic parameters:
* `population`: The population which needs to evolve. Each subject (or element) in the
 population is represented as a sequence of values
* `all_values`: A sequence of all the possible values (genes) allowed in each subject of the population
* `strength_function`: A function that accepts a subject of the population and determines 
 its strength, in the range of [0, inf], the higher the strength is, the closer the subject is to the 
 desired state
* `offspring_function`: A function that accepts two subjects (parents) 
 and outputs two subjects (offspring). The `offspring_functions` module holds some that can be used

More configurations:
* `elitism_ratio`: Must be in the range of [0,1]. Determines the percentage of elitists in each 
 iteration. Elitists are the strongest subject in their generation, and therefore survive and advance 
 untouched to the next generation (mutation can still apply). Default value: 0.1
* `mutations_odds`: Must be in the range of [0,1]. Determines the probability for mutation of 
 the subjects in each generation. A mutation is a single binary bit in the subject's genes being randomly
 flipped. Default value: 0.001
* `generations`: Must be a positive integer. The number of iterations the model should run through
 before stopping. Default value: 10
* `duplication_policy`: The policy of the model regarding duplicates in the population. See
 the class's documentation for more info. 
* `seed` = A seed to be supplied to the model's pseudo-random number generator. Default value:
 system time (`int(time.time())`)
 
## Examples:
Examples are found in the project's test directory, in the `examples` module.

### Reach 42:
Each subject in the population is a mathematical equation, made of four integers from 0 to 9 and three
operators from `[+,-,*,/]`. Each subject is represented as sequence of single-character strings of either
a digit or an operator. The model's objective is to find a set of digits and characters which will
yield 42. The Strength Function is defined as the absolute value of the result of 1/(x-42).

### License:
Apache License 2.0