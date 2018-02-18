from __future__ import division
import math
import operator
import random
import time
import offspring_functions
from model import Model
from functools import partial
from pyparsing import (Literal, CaselessLiteral, Word, Combine, Group, Optional, ZeroOrMore, Forward, nums, alphas, oneOf)


class NumericStringParser:
    __author__ = 'Paul McGuire'
    __version__ = '$Revision: 0.0 $'
    __date__ = '$Date: 2009-03-20 $'
    __source__ = '''http://pyparsing.wikispaces.com/file/view/fourFn.py
    http://pyparsing.wikispaces.com/message/view/home/15549426
    '''
    __note__ = '''
    Original code taken from https://stackoverflow.com/a/2371789/5863503 on 18/02/2018
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
    def strength(subject, calculator):
        try:
            result = calculator.eval(''.join(subject))
            if result == 42.0:
                return math.inf
            else:
                return abs(1/(result-42.0))
        except:
            return 0.0

    def strength_func(calculator):
        return partial(strength, calculator=calculator)

    def calc(subject, calculator):
        try:
            return calculator.eval(''.join(subject))
        except:
            return "NaN"

    seed = 1518883307
    random.seed(seed)
    calculator = NumericStringParser()
    all_values = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "+", "-", "*", "/"]
    population = list()
    for _ in range(0,30):
        subject = list()
        for i in range(0,7):
            if i%2 == 0:
                r = random.randint(0,9)
            else:
                r = random.randint(10,13)
            subject.append(all_values[r])
        population.append(subject)
    print('Reach 42 - Starting population:\n----------------------------------')
    for subject in population:
        print(' '.join(subject), " = ", calc(subject,calculator))
    model = Model(population,all_values,strength_func(calculator),offspring_functions.slice_and_stitch_func(all_values),
                  seed=seed)
    model.evolve()

    print('----------------------------------')
    print('Evolution end cause: {0} [Reason ID: {1}]'.format(model.get_end_reason()[1],model.get_end_reason()[0]))
    print('Iterations required:', model.get_current_generation())
    print("Model's best result: {0}  =  {1}".format(' '.join(model.get_best()),calc(model.get_best(),calculator)))


reach_42()

