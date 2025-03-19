from abc import ABC, abstractmethod
from copy import deepcopy


class StateFormula(ABC):
    @abstractmethod
    def eliminate_negation(self):
        pass


class AtomicFormula(StateFormula):
    @abstractmethod
    def yield_dov(self, dov, max_activities):
        pass


class AtomicProposition(AtomicFormula):
    def __init__(self, variable, operator, value):
        self.variable = variable
        self.operator = operator
        self.value = value

    def __repr__(self):
        return f"({self.variable} {self.operator} {self.value})"

    def yield_dov(self, dov, max_activities):
        new_dov = deepcopy(dov)
        idx = list(max_activities.keys()).index(self.variable)
        max_val = max_activities[self.variable]

        if self.operator == ">=":
            # Valid values are from self.value to max_val
            valid_values = list(range(max(self.value, 0), max_val + 1))
        elif self.operator == "<=":
            # Valid values are from 0 to self.value
            valid_values = list(range(0, min(self.value, max_val) + 1))
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")

        # Intersect existing dov with valid_values
        new_dov[idx] = sorted(set(new_dov[idx]).intersection(valid_values))

        return new_dov

    def eliminate_negation(self):
        if self.operator == ">=":
            return AtomicProposition(self.variable, "<=", self.value - 1)
        elif self.operator == "<=":
            return AtomicProposition(self.variable, ">=", self.value + 1)
        else:
            raise ValueError(f"Unsupported operator '{self.operator}' for negation.")


class Negation(AtomicFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"!{repr(self.operand)}"

    def yield_dov(self, dov, max_activities):
        raise NotImplementedError("Negation must be eliminated before calling yield_dov.")

    def eliminate_negation(self):
        if isinstance(self.operand, AtomicProposition):
            return self.operand.eliminate_negation()
        elif isinstance(self.operand, Negation):
            return self.operand.operand.eliminate_negation()
        elif isinstance(self.operand, Union):
            left_neg = Negation(self.operand.left).eliminate_negation()
            right_neg = Negation(self.operand.right).eliminate_negation()
            return Intersection(left_neg, right_neg)
        elif isinstance(self.operand, Intersection):
            left_neg = Negation(self.operand.left).eliminate_negation()
            right_neg = Negation(self.operand.right).eliminate_negation()
            return Union(left_neg, right_neg)
        else:
            raise ValueError("Unsupported operand type in Negation elimination.")


class Union(AtomicFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} | {repr(self.right)})"

    def yield_dov(self, dov, max_activities):
        left_dov = self.left.yield_dov(dov, max_activities)
        right_dov = self.right.yield_dov(dov, max_activities)

        combined_dov = []
        for idx in range(len(dov)):
            # Union: merge values from both sides
            combined = sorted(set(left_dov[idx]).union(right_dov[idx]))
            combined_dov.append(combined)

        return combined_dov

    def eliminate_negation(self):
        new_left = self.left.eliminate_negation()
        new_right = self.right.eliminate_negation()
        return Union(new_left, new_right)


class Intersection(AtomicFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} & {repr(self.right)})"

    def yield_dov(self, dov, max_activities):
        left_dov = self.left.yield_dov(dov, max_activities)
        right_dov = self.right.yield_dov(dov, max_activities)

        combined_dov = []
        for idx in range(len(dov)):
            # Intersection: take common values from both sides
            combined = sorted(set(left_dov[idx]).intersection(right_dov[idx]))
            combined_dov.append(combined)

        return combined_dov

    def eliminate_negation(self):
        new_left = self.left.eliminate_negation()
        new_right = self.right.eliminate_negation()
        return Intersection(new_left, new_right)



class Boolean(StateFormula):
    def __init__(self, value):
        self.value = value  # True or False

    def __repr__(self):
        return str(self.value)

    def eval(self):
        pass  # Placeholder for evaluation logic

    def eliminate_negation(self):
        # Nothing to do for a Boolean; return itself
        return self


class Conjunction(StateFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} && {repr(self.right)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        # Propagate to children
        left = self.left.eliminate_negation()
        right = self.right.eliminate_negation()
        return Conjunction(left, right)


class Disjunction(StateFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({repr(self.left)} || {repr(self.right)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        left = self.left.eliminate_negation()
        right = self.right.eliminate_negation()
        return Disjunction(left, right)


class AG(StateFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"AG ({repr(self.operand)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        operand = self.operand.eliminate_negation()
        return AG(operand)


class AF(StateFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"AF ({repr(self.operand)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        operand = self.operand.eliminate_negation()
        return AF(operand)


class AX(StateFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"AX ({repr(self.operand)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        operand = self.operand.eliminate_negation()
        return AX(operand)


class AU(StateFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"A ({repr(self.left)}) U ({repr(self.right)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        left = self.left.eliminate_negation()
        right = self.right.eliminate_negation()
        return AU(left, right)


class EG(StateFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"EG ({repr(self.operand)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        operand = self.operand.eliminate_negation()
        return EG(operand)


class EF(StateFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"EF ({repr(self.operand)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        operand = self.operand.eliminate_negation()
        return EF(operand)


class EX(StateFormula):
    def __init__(self, operand):
        self.operand = operand

    def __repr__(self):
        return f"EX ({repr(self.operand)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        operand = self.operand.eliminate_negation()
        return EX(operand)


class EU(StateFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"E ({repr(self.left)}) U ({repr(self.right)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        left = self.left.eliminate_negation()
        right = self.right.eliminate_negation()
        return EU(left, right)


class AW(StateFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"A ({repr(self.left)}) W ({repr(self.right)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        left = self.left.eliminate_negation()
        right = self.right.eliminate_negation()
        return AW(left, right)


class EW(StateFormula):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"E ({repr(self.left)}) W ({repr(self.right)})"

    def eval(self):
        pass

    def eliminate_negation(self):
        left = self.left.eliminate_negation()
        right = self.right.eliminate_negation()
        return EW(left, right)
