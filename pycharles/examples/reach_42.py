from __future__ import division
import math
import operator
import random
from pycharles import offspring_functions
from pycharles.model import Model
from functools import partial
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf)


# Original class-code taken from: https://stackoverflow.com/a/2371789/5863503
class NumericStringParser:
    __author__ = 'Paul McGuire'
    __version__ = '$Revision: 0.0 $'
    __date__ = '$Date: 2009-03-20 $'
    __source__ = '''http://pyparsing.wikispaces.com/file/view/fourFn.py
    http://pyparsing.wikispaces.com/message/view/home/15549426
    '''
    __note__ = '''
    All I've done is rewrap Paul McGuire's fourFn.py as a class, so I can use it
    more easily in other places.
    '''

    def pushFirst(self, strg, loc, toks):
        self.exprStack.append(toks[0])

    def pushUMinus(self, strg, loc, toks):
        if toks and toks[0] == '-':
            self.exprStack.append('unary -')

    def __init__(self):
        point = Literal(".")
        e = CaselessLiteral("E")
        fnumber = Combine(Word("+-" + nums, nums) +
                          Optional(point + Optional(Word(nums))) +
                          Optional(e + Word("+-" + nums, nums)))
        ident = Word(alphas, alphas + nums + "_$")
        plus = Literal("+")
        minus = Literal("-")
        mult = Literal("*")
        div = Literal("/")
        lpar = Literal("(").suppress()
        rpar = Literal(")").suppress()
        addop = plus | minus
        multop = mult | div
        expop = Literal("^")
        pi = CaselessLiteral("PI")
        expr = Forward()
        atom = ((Optional(oneOf("- +")) +
                 (ident + lpar + expr + rpar | pi | e | fnumber).setParseAction(self.pushFirst))
                | Optional(oneOf("- +")) + Group(lpar + expr + rpar)
                ).setParseAction(self.pushUMinus)
        factor = Forward()
        factor << atom + \
            ZeroOrMore((expop + factor).setParseAction(self.pushFirst))
        term = factor + \
            ZeroOrMore((multop + factor).setParseAction(self.pushFirst))
        expr << term + \
            ZeroOrMore((addop + term).setParseAction(self.pushFirst))
        self.bnf = expr
        self.opn = {"+": operator.add,
                    "-": operator.sub,
                    "*": operator.mul,
                    "/": operator.truediv,
                    "^": operator.pow}
        self.fn = {}

    def evaluateStack(self, s):
        op = s.pop()
        if op == 'unary -':
            return -self.evaluateStack(s)
        if op in "+-*/^":
            op2 = self.evaluateStack(s)
            op1 = self.evaluateStack(s)
            return self.opn[op](op1, op2)
        elif op == "PI":
            return math.pi  # 3.1415926535
        elif op == "E":
            return math.e  # 2.718281828
        elif op in self.fn:
            return self.fn[op](self.evaluateStack(s))
        elif op[0].isalpha():
            return 0
        else:
            return float(op)

    def eval(self, num_string, parseAll=True):
        self.exprStack = []
        results = self.bnf.parseString(num_string, parseAll)
        val = self.evaluateStack(self.exprStack[:])
        return val


def reach_42():
    """
    In this example, the population is made out of 30 combinations of simple mathematical equations. Each
    equation is constructed of four integers from 0 to 9, separated by one of four mathematical operators:
    [+,-,/,*]. The goal of the model is to construct such mathematical equation which will yield 42.
    """
    calculator = NumericStringParser()

    def strength(subject, calculator):
        """
        This is the strength function which will be supplied to the model. The strength is calculated as
        abs(1/(42-x)) for any given x.
        calculator is an instance of NumericStringParser which is used to compute the mathematical result
        out of a string of numbers and operators.

        :param subject: the subject to evaluate
        :param calculator: an instance of NumericStringParser
        :return: calculated strength
        """
        try:
            result = calculator.eval(''.join(subject))
            if result == 42.0:
                return math.inf
            else:
                return abs(1/(result-42.0))
        except:
            return 0.0

    def strength_func(calculator):
        """
        This function created a partial function of strength to be used by the model.

        :param calculator: an instance of NumericStringParser
        :return: a partial function of strength
        """
        return partial(strength, calculator=calculator)

    def calc(subject, calculator):
        try:
            return calculator.eval(''.join(subject))
        except:
            return "NaN"

    def run_model(population, all_values, seed):
        print('Starting population:\n----------------------------------')
        for subject in population:
            print(' '.join(subject), " = ", calc(subject, calculator))
        model = Model(population, all_values, strength_func(calculator),
                      seed=seed, verbose=True)
        print('----------------------------------')
        model.evolve()
        print('----------------------------------')
        print("Model's best result: {0}  =  {1}\n".format(' '.join(model.get_best()), calc(model.get_best(), calculator)))

    print('** REACH 42 **')

    # values are a list
    seed = 1519568369
    random.seed(seed)
    all_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/"]
    population = list()
    for _ in range(0, 30):
        subject = list()
        for i in range(0, 7):
            if i % 2 == 0:
                r = random.randint(0, 9)
            else:
                r = random.randint(10, 13)
            subject.append(all_values[r])
        population.append(subject)
    print('>> Values are a list:\n',all_values)
    run_model(population,all_values,seed)

    # values are a dict
    seed = 1519568346
    random.seed(seed)
    all_values = {0: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                  2: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                  4: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                  6: ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9"],
                  1: ["+", "-", "*", "/"],
                  3: ["+", "-", "*", "/"],
                  5: ["+", "-", "*", "/"]}
    population = list()
    for _ in range(0,30):
        subject = list()
        for i in range(0,7):
            if i%2 == 0:
                r = random.randint(0,9)
            else:
                r = random.randint(0,3)
            subject.append(all_values[i][r])
        population.append(subject)
    print('>> Values are a dict:')
    positions = list(all_values.keys())
    positions.sort()
    for p in positions:
        print(p,':',all_values[p])
    run_model(population,all_values,seed)
