from abc import ABC, abstractmethod
from copy import deepcopy
from src.quantitative_ctl import KripkeStructure
from src.satisfaction_degree import weighted_signed_distance, find_extreme_state
from src.custom_types import *



class StateFormula(ABC):
    @abstractmethod
    def eliminate_negation(self) -> 'StateFormula':
        pass

    @abstractmethod
    def get_subformulae(self) -> List['StateFormula']:
        pass

    @abstractmethod
    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class AtomicFormula(StateFormula):
    @abstractmethod
    def yield_dov(self, dov: DomainOfValidity, max_activities: MaxActivitiesType) -> DomainOfValidity:
        pass

    def get_subformulae(self) -> List['StateFormula']:
        return [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        # To be implemented
        pass


class AtomicProposition(AtomicFormula):

    def __init__(self, variable: str, operator: str, value: int) -> None:
        self.variable = variable
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f"({self.variable} {self.operator} {self.value})"

    def yield_dov(self, dov: DomainOfValidity, max_activities: MaxActivitiesType) -> DomainOfValidity:
        new_dov = deepcopy(dov)
        idx = list(max_activities.keys()).index(self.variable)
        max_val = max_activities[self.variable]

        if self.operator == ">=":
            valid_values = list(range(max(self.value, 0), max_val + 1))
        elif self.operator == "<=":
            valid_values = list(range(0, min(self.value, max_val) + 1))
        else:
            raise ValueError(f"Unsupported operator: {self.operator}")

        new_dov[idx] = sorted(set(new_dov[idx]).intersection(valid_values))
        return new_dov

    def eliminate_negation(self) -> 'AtomicFormula':
        if self.operator == ">=":
            return AtomicProposition(self.variable, "<=", self.value - 1)
        elif self.operator == "<=":
            return AtomicProposition(self.variable, ">=", self.value + 1)
        else:
            raise ValueError(f"Unsupported operator '{self.operator}' for negation.")



class Negation(AtomicFormula):
    def __init__(self, operand: AtomicFormula) -> None:
        self.operand = operand

    def __repr__(self) -> str:
        return f"!{repr(self.operand)}"

    def yield_dov(self, dov: DomainOfValidity, max_activities: MaxActivitiesType) -> DomainOfValidity:
        raise NotImplementedError("Negation must be eliminated before calling yield_dov.")

    def eliminate_negation(self) -> AtomicFormula:
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

    def get_subformulae(self) -> List['StateFormula']:
        raise NotImplementedError("Negation must be eliminated before calling get_subformulae.")


class Union(AtomicFormula):
    def __init__(self, left: AtomicFormula, right: AtomicFormula) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} | {repr(self.right)})"

    def yield_dov(self, dov: DomainOfValidity, max_activities: MaxActivitiesType) -> DomainOfValidity:
        left_dov = self.left.yield_dov(dov, max_activities)
        right_dov = self.right.yield_dov(dov, max_activities)

        combined_dov = [
            sorted(set(left_dov[idx]).union(right_dov[idx]))
            for idx in range(len(dov))
        ]

        return combined_dov

    def eliminate_negation(self) -> AtomicFormula:
        return Union(self.left.eliminate_negation(), self.right.eliminate_negation())


class Intersection(AtomicFormula):
    def __init__(self, left: AtomicFormula, right: AtomicFormula) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} & {repr(self.right)})"

    def yield_dov(self, dov: DomainOfValidity, max_activities: MaxActivitiesType) -> DomainOfValidity:
        left_dov = self.left.yield_dov(dov, max_activities)
        right_dov = self.right.yield_dov(dov, max_activities)
        combined_dov = [
            sorted(set(left_dov[idx]).intersection(right_dov[idx]))
            for idx in range(len(dov))]
        return combined_dov

    def eliminate_negation(self) -> AtomicFormula:
        return Intersection(self.left.eliminate_negation(), self.right.eliminate_negation())


class Boolean(StateFormula):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)

    def eliminate_negation(self) -> 'StateFormula':
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class Conjunction(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} && {repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        return Conjunction(self.left.eliminate_negation(), self.right.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        # To be implemented
        pass


class Disjunction(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} || {repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        return Disjunction(self.left.eliminate_negation(), self.right.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        # To be implemented
        pass


# Temporal Operators
class AG(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"AG ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        return AG(self.operand.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        # To be implemented
        pass


class AF(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"AF ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        return AF(self.operand.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class AX(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"AX ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        return AX(self.operand.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class AU(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"A ({repr(self.left)}) U ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        return AU(self.left.eliminate_negation(), self.right.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class EG(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"EG ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        return EG(self.operand.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class EF(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"EF ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        return EF(self.operand.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class EX(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"EX ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        return EX(self.operand.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class EU(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"E ({repr(self.left)}) U ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        return EU(self.left.eliminate_negation(), self.right.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class AW(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"A ({repr(self.left)}) W ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        return AW(self.left.eliminate_negation(), self.right.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass


class EW(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"E ({repr(self.left)}) W ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        return EW(self.left.eliminate_negation(), self.right.eliminate_negation())

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, mc_data: MCDataType) -> None:
        pass
