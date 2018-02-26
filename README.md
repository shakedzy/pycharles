# PyCharles
A Genetic-Model library in **Python 3.x**. 

This library is based on the original [Charles library in Scala](https://github.com/shakedzy/charles).

![Charles Darwin](https://i.guim.co.uk/img/media/83381c9b4b97c3eefd1c6f67cd32f819e22fab80/60_206_3398_4246/master/3398.jpg?w=300&q=55&auto=format&usm=12&fit=max&s=d3ece4b003774449dc14053a243597a9)

_Charles Darwin, 1809-1882_

### Some reading and examples:
* [Genetic Algorithms on Wikipedia](https://en.wikipedia.org/wiki/Genetic_algorithm)
* This [blog post](https://burakkanber.com/blog/machine-learning-genetic-algorithms-part-1-javascript/) with a simple tutorial and an example

## Installation:
Clone this repository to your local machine anr run `pip`:
```
git clone https://github.com/shakedzy/pycharles.git
cd pycharles
pip install .
```

## Usage:
Quick start:
```
from pycharles import Model
model = Model(population, all_values, strength_function, offspring_function)
model.evolve()
solution = model.get_best()
```
Basic parameters:
* `population`: The population which needs to evolve. Each subject (or element) in the
 population is represented as a sequence of values
* `all_values`: All the possible values (genes) allowed in each subject of the population. This can either
be a `list`, in which case all values are drawn from the same pool, or a `dict`, where the keys are integers
representing the indices of the values of the subject, and the values are `list`s representing the unique 
pools for each index.
* `strength_function`: A function that accepts a subject of the population and determines 
 its strength, in the range of [0, inf], the higher the strength is, the closer the subject is to the 
 desired state
* `offspring_function`: A function that accepts two subjects (parents) 
 and outputs two subjects (offspring). The `offspring_functions` module holds some that can be used 
 (use `from pycharles import offspring_functions`)

More configurations:
* `elitism_ratio`: Must be in the range of [0,1]. Determines the percentage of elitists in each 
 iteration. Elitists are the strongest subject in their generation, and therefore survive and advance 
 untouched to the next generation. Default value: 0.1
* `mutations_odds`: Must be in the range of [0,1]. Determines the probability for mutation of 
 the subjects in each generation. A mutation is a single binary bit in the subject's genes being randomly
 flipped. Default value: 0.001 
* `generations`: Must be a positive integer. The number of iterations the model should run through
 before stopping. Default value: 10
* `early_stop`: Must be a positive integer or None (0 is the same as None). When not None, The model
 will stop if a better solution was not found after the amount of generations specified. Default: None
* `duplication_policy`: The policy of the model regarding duplicates in the population at the end of 
 each generation. Options are: (1) `ignore`, ignore the duplications, (2) `kill`, leave only one copy of
 each duplicated value. This shrinks the size of the population, (3) `replace`, similar to `kill`, only
 the model will let the population breed again in order to fill the missing values. If any duplications occur
 after this process, the model will repeat this process until all values are unique or up to 3 attempts, after
 which the model will ignore duplications and proceed. To change the maximum attempts the model will make to
 replace duplications, use `replace:X`, where `X` is the desired number. Default: `ignore` 
* `mutate_elitists`: Boolean. Set if elitists can mutate when transferring from one generation to
 the next one. When False, this ensures that the top solutions will be remain unchanged. When True, this
  allows the model to explore more solutions. Default: False
* `seed`: A seed to be supplied to the model's pseudo-random number generator. Default value:
 system time (`int(time.time())`)
* `verbose`: Boolean. Set verbosity level. Default: False
 
## Examples:
Examples are found in the project's test directory, in the `examples` module.

### Reach 42:
Each subject in the population is a mathematical equation, made of four integers from 0 to 9 and three
operators from `[+,-,*,/]`. Each subject is represented as sequence of single-character strings of either
a digit or an operator. The model's objective is to find a set of digits and characters which will
yield 42. The Strength Function is defined as the absolute value of the result of 1/(x-42).

### TO DO:
* Code documentation

### License:
Apache License 2.0