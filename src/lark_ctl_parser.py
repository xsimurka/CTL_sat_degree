from lark import Lark, Transformer
from diplomka.src.ctl_formulae import *


grammar = r"""
    start: state_formula

    ?state_formula: "AG" "(" state_formula ")"    -> ag
                  | "AF" "(" state_formula ")"    -> af
                  | "AX" "(" state_formula ")"    -> ax
                  | "EG" "(" state_formula ")"    -> eg
                  | "EF" "(" state_formula ")"    -> ef
                  | "EX" "(" state_formula ")"    -> ex
                  | "A" "(" state_formula ")" "U" "(" state_formula ")" -> au
                  | "E" "(" state_formula ")" "U" "(" state_formula ")" -> eu
                  | "A" "(" state_formula ")" "W" "(" state_formula ")" -> aw
                  | "E" "(" state_formula ")" "W" "(" state_formula ")" -> ew
                  | state_formula "&" state_formula -> conjunction
                  | state_formula "|" state_formula -> disjunction
                  | atomic_formula

    ?atomic_formula: negation
                   | atomic_and
                   | atomic_or
                   | ap
                   | parenthesis

    negation: "!" "(" atomic_formula ")" -> negation

    atomic_and: atomic_formula "&" atomic_formula -> intersection
    atomic_or: atomic_formula "|" atomic_formula -> union

    ap: CNAME OPERATOR VALUE -> ap

    parenthesis: "(" state_formula ")" -> parenthesis

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
parser = Lark(grammar, start='start', parser='lalr', transformer=FormulaTransformer())

# Example usage
examples = [
    "(x >= 1) | (y >= 2)",
    "AF (x >= 1) | (y >= 2)",
    "AG (x1 >= 3)",
    "AF (x2 <= 4 | x3 >= 5)",
    "AX (!(x4 <= 7 & x5 >= 2))",
    "A (x1 >= 2) U (EG (x2 >= 1))",
    "E (AG (x3 <= 5)) W (EF (x4 >= 8))",
    "!(x1 <= 3 & x2 >= 7)",
    "!(x1 >= 2 | x2 <= 6)",
    "(x1 >= 2) & (x2 <= 3)",
    "!(x1 >= 3)",
]

for i, example in enumerate(examples, 1):
    print(f"\nExample {i}: {example}")
    try:
        tree = parser.parse(example)
        print(tree.children[0])
    except Exception as e:
        print(f"Error parsing: {e}")
