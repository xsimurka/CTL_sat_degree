from lark import Lark, Transformer
from src.ctl_formulae import AtomicProposition, Negation, Union, Intersection, Conjunction, Disjunction, EX, AX, EF, AF, \
    EG, AG, EU, AU, EW, AW

grammar = r"""
    start: state_formula

    ?state_formula : state_formula_c
                  | atomic_formula "&&" state_formula_c -> conjunction
                  | atomic_formula "||" state_formula_c -> disjunction 
                  | "(" state_formula ")" -> parenthesis
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

    ap: NAME OPERATOR VALUE -> ap

    OPERATOR: "<=" | ">="
    VALUE: /[0-9]+/
    NAME: /[a-zA-Z_][a-zA-Z0-9_]*/

    %import common.NUMBER
    %import common.WS
    %ignore WS
"""


class FormulaTransformer(Transformer):
    """
    Transforms a parsed formula tree into the corresponding StateFormula objects.

    @param args: List of arguments (children nodes) from the parsing tree.
    @return: Transformed object (StateFormula).
    """

    def ap(self, args):
        """
        Transforms atomic proposition into an AtomicProposition object.

        @param args: List of arguments [variable_name, operator, value] for the atomic proposition.
        @return: AtomicProposition object.
        """
        variable_name, operator, value = args
        return AtomicProposition(str(variable_name), str(operator), int(value))

    def negation(self, args):
        """
        Transforms negation into a Negation object.

        @param args: List containing the negated formula.
        @return: Negation object.
        """
        return Negation(args[0])

    def union(self, args):
        """
        Transforms union (|) into a Union object.

        @param args: List of arguments [formula_1, formula_2] for the union operation.
        @return: Union object.
        """
        return Union(args[0], args[1])

    def intersection(self, args):
        """
        Transforms intersection (&) into an Intersection object.

        @param args: List of arguments [formula_1, formula_2] for the intersection operation.
        @return: Intersection object.
        """
        return Intersection(args[0], args[1])

    def conjunction(self, args):
        """
        Transforms conjunction (&&) into a Conjunction object.

        @param args: List of arguments [formula_1, formula_2] for the conjunction operation.
        @return: Conjunction object.
        """
        return Conjunction(args[0], args[1])

    def disjunction(self, args):
        """
        Transforms disjunction (||) into a Disjunction object.

        @param args: List of arguments [formula_1, formula_2] for the disjunction operation.
        @return: Disjunction object.
        """
        return Disjunction(args[0], args[1])

    def ag(self, args):
        """
        Transforms AG (always globally) into an AG object.

        @param args: List containing the formula to be globally true.
        @return: AG object.
        """
        return AG(args[0])

    def af(self, args):
        """
        Transforms AF (always eventually) into an AF object.

        @param args: List containing the formula to be eventually true.
        @return: AF object.
        """
        return AF(args[0])

    def ax(self, args):
        """
        Transforms AX (always next) into an AX object.

        @param args: List containing the formula to be true at the next state.
        @return: AX object.
        """
        return AX(args[0])

    def eg(self, args):
        """
        Transforms EG (exists globally) into an EG object.

        @param args: List containing the formula to exist globally.
        @return: EG object.
        """
        return EG(args[0])

    def ef(self, args):
        """
        Transforms EF (exists eventually) into an EF object.

        @param args: List containing the formula to exist eventually.
        @return: EF object.
        """
        return EF(args[0])

    def ex(self, args):
        """
        Transforms EX (exists next) into an EX object.

        @param args: List containing the formula to exist in the next state.
        @return: EX object.
        """
        return EX(args[0])

    def au(self, args):
        """
        Transforms AU (always until) into an AU object.

        @param args: List containing the formulas to be true until a condition is met.
        @return: AU object.
        """
        return AU(args[0], args[1])

    def eu(self, args):
        """
        Transforms EU (exists until) into an EU object.

        @param args: List containing the formulas to exist until a condition is met.
        @return: EU object.
        """
        return EU(args[0], args[1])

    def aw(self, args):
        """
        Transforms AW (always weakly until) into an AW object.

        @param args: List containing the formulas to be true weakly until a condition is met.
        @return: AW object.
        """
        return AW(args[0], args[1])

    def ew(self, args):
        """
        Transforms EW (exists weakly until) into an EW object.

        @param args: List containing the formulas to exist weakly until a condition is met.
        @return: EW object.
        """
        return EW(args[0], args[1])

    def parenthesis(self, args):
        """
        Returns the formula inside parentheses without modification.

        @param args: List containing the formula inside parentheses.
        @return: The formula inside parentheses.
        """
        return args[0]


def parse_formula(formula):
    """
    Parses a CTL formula string and returns the corresponding formula tree.

    @param formula: The CTL formula string to be parsed.
    @return: The parsed StateFormula object.
    """
    parser = Lark(grammar, start='start', parser='lalr', transformer=FormulaTransformer())
    tree = parser.parse(formula)
    return tree.children[0]
