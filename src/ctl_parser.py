import re
from src.ctl_formulae import *


class CTLParser:
    def __init__(self):
        self.tokens = []
        self.pos = 0
        self.unary_operators = {
            '!': Negation,
            'AG': AG,
            'AF': AF,
            'EG': EG,
            'EF': EF,
            'AX': AX,
            'EX': EX
        }
        self.binary_operators = {
            'AU': AU,
            'EU': EU,
            'AW': AW,
            'EW': EW
        }

    def parse(self, formula):
        """Public method for parsing CTL formulas"""
        self.tokens = re.findall(r'true|false|AX|EX|AF|EF|AG|EG|A|E|U|[A-Za-z0-9_]+|[()!&|]|>=|<=|\d+', formula)
        self.pos = 0
        return self._parse_disjunction()  # start with lowest priority operator

    def _parse_disjunction(self):
        """Parses disjunctions grouped from the left, recursively calls parsing of higher priority operators"""

        left = self._parse_conjunction()  # parse subexpression to the left
        while self._consume('|'):  # all disjunctions are handled here, arguments are of higher priority
            right = self._parse_conjunction()  # look for expressions of higher priority
            left = Disjunction(left, right)  # disjunction found, the outermost is on the very left
        return left  # if no (more) disjunctions present return the parsed expression

    def _parse_conjunction(self):
        """Parses conjunctions grouped from the left, recursively calls parsing of higher priority operators"""
        left = self._parse_ctl_operator()  # parse subexpression to the left
        while self._consume('&'):  # all conjunctions are handled here, arguments are of higher priority
            right = self._parse_ctl_operator()  # look for expressions of higher priority
            left = Conjunction(left, right)  # conjunction found, the outermost is on the very left
        return left  # if no (more) conjunctions present return the parsed expression

    def _parse_ctl_operator(self):
        """Parses CTL operators, recursively calls parsing of nested unary operator or atomic proposition"""
        token = self._get_current()
        if token in self.unary_operators:
            self.pos += 1
            operator_class = self.unary_operators[token]
            return operator_class(self._parse_ctl_operator())

        if token in {'A', 'E'}:
            self.pos += 1
            left = self._parse_ctl_operator()
            found = self._expect({'U', 'W'})
            right = self._parse_ctl_operator()
            operator_class = self.binary_operators[token + found]
            return operator_class(left, right)

        if self._consume('('):
            expr = self._parse_disjunction()  # parse any kind of subexpression closed in brackets
            self._expect({')'})
            return expr

        if self._consume('true'):
            return Boolean(True)

        if self._consume('false'):
            return Boolean(False)

        return self._parse_atomic_proposition()

    def _parse_atomic_proposition(self):
        """Parses atomic propositions"""
        if re.match(r'[A-Za-z0-9_]+', self._get_current()) and self._get_next() in {'>=', '<='}:
            variable = self._get_current()
            operator = self.tokens[self.pos + 1]
            self.pos += 2

            if self.pos < len(self.tokens) and re.match(r'\d+', self.tokens[self.pos]):
                value = int(self.tokens[self.pos])
                self.pos += 1
                return AtomicProposition(variable, operator, value)
            else:
                raise ValueError(f"P{self.pos}: Expected integer value after operator")

        raise ValueError(f"P{self.pos}: Invalid atomic proposition format")

    def _expect(self, expected):
        """Looks for expected token belonging to currently parsed operator"""
        if self.pos >= len(self.tokens) or self.tokens[self.pos] not in expected:
            raise ValueError(f"P{self.pos}: Expected '{expected}', found '{self.tokens[self.pos]}'")
        found = self.tokens[self.pos]
        self.pos += 1
        return found

    def _consume(self, token):
        """Checks for matches of given token and consumes it if found"""
        if self.pos < len(self.tokens) and self.tokens[self.pos] == token:
            self.pos += 1
            return True

        return False

    def _get_next(self):
        """Returns token on the next position"""
        return self.tokens[self.pos + 1] if self.pos + 1 < len(self.tokens) else None

    def _get_current(self):
        """Returns token on the current position"""
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None
