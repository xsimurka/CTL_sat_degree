from lark import Lark, Transformer
from src.ctl_formulae import *


grammar = r"""
    
    start: state_formula

    ?state_formula : state_formula_c
                  | atomic_formula "&&" state_formula_c -> conjunction
                  | atomic_formula "||" state_formula_c -> disjunction
                  | state_formula_c "&&" atomic_formula -> conjunction
                  | state_formula_c "||" atomic_formula -> disjunction
                  | "(" state_formula ")" //-> parenthesis
                  | atomic_formula
                  
    ?state_formula_c : state_formula_c "&&" state_formula_c -> conjunction
                  | state_formula_c "||" state_formula_c -> disjunction
                  | "AG" state_formula   -> ag
                  | "AF" state_formula   -> af
                  | "AX" state_formula   -> ax
                  | "EG" state_formula   -> eg
                  | "EF" state_formula   -> ef
                  | "EX" state_formula   -> ex
                  | "A" state_formula "U" state_formula -> au
                  | "E" state_formula "U" state_formula -> eu
                  | "A" state_formula "W" state_formula  -> aw
                  | "E" state_formula "W" state_formula -> ew
                  | "(" state_formula_c ")" -> parenthesis
                  
    ?atomic_formula : "!" atomic_formula -> negation
                   | atomic_formula "&" atomic_formula -> intersection
                   | atomic_formula "|" atomic_formula -> union
                   | ap
                   | "(" atomic_formula ")" -> parenthesis

    ap: CNAME OPERATOR VALUE -> ap

    OPERATOR: "<=" | ">="
    VALUE: /[0-9]+/
    CNAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""


class FormulaTransformer(Transformer):
    def ap(self, args):
        variable, operator, value = args
        return AtomicProposition(variable, operator, value)

    def negation(self, args):
        # Wrap only the atomic proposition inside negation
        return Negation(args[0])

    def union(self, args):
        return Union(args[0], args[1])

    def intersection(self, args):
        return Intersection(args[0], args[1])

    def conjunction(self, args):
        return Conjunction(args[0], args[1])

    def disjunction(self, args):
        return Disjunction(args[0], args[1])

    def ag(self, args):
        return AG(args[0])

    def af(self, args):
        return AF(args[0])

    def ax(self, args):
        return AX(args[0])

    def eg(self, args):
        return EG(args[0])

    def ef(self, args):
        return EF(args[0])

    def ex(self, args):
        return EX(args[0])

    def au(self, args):
        return AU(args[0], args[1])

    def eu(self, args):
        return EU(args[0], args[1])

    def aw(self, args):
        return AW(args[0], args[1])

    def ew(self, args):
        return EW(args[0], args[1])

    def parenthesis(self, args):
        # When parentheses are used, we return the wrapped state formula.
        return args[0]


# Create the parser


examples = [
    # Conjunction of two state formulas
    "AG (x1 >= 1) && EF (x2 <= 5)",

    # Disjunction of two state formulas
    "AX (x3 >= 2) || EG (x4 <= 7)",

    # A temporal operator on a conjunction of two state formulas
    "AF (AG (x1 >= 3) && EF (x2 <= 2))",

    # Conjunction of atomic and state formula (mix)
    "(x1 >= 2) && AF (x2 >= 1)",

    # Disjunction of atomic and state formula (mix)
    "(x3 <= 4) || EG (x5 >= 8)",

    # Nested temporal operators with conjunction inside
    "AG (AX (x1 >= 2) && EX (x2 <= 7))",

    # Until operator where left is a state formula and right is an atomic proposition
    "A (AG (x1 >= 4)) U (x2 <= 3)",

    # Weak until with mixed atomic/state formulas
    "E (x1 >= 2) W (AF (x3 <= 6))",

    # Negation of conjunction of a state formula and an atomic proposition
    "EG (x1 >= 4) & !(x2 <= 5)",

    # Nested negation and union inside temporal operators
    "AF (!(x1 >= 4 | x2 <= 3))",

    # Deeply nested temporal operators with conjunctions
    "EG (AF (AX (x1 >= 5) && EX (x2 <= 6)))",

    # Disjunction at the top level combining state formulas
    "AF (x1 >= 3) || EG (x2 <= 8)",

    # Negation of disjunction of two state formulas
    "(AF !(x1 >= 3) || EF (x2 <= 4))"
]


def parse_formula(formula):
    parser = Lark(grammar, start='start', parser='lalr', transformer=FormulaTransformer())
    tree = parser.parse(formula)
    return tree.children[0]
