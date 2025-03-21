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
        dov = [list(range(max_value + 1)) for max_value in ks.stg.variables.values()]
        for state in ks.stg.states:
            d = self.yield_dov(dov, ks.stg.variables)
            wsd = weighted_signed_distance(d, state, ks.stg.variables.values())
            ext_s, ext_wsd = find_extreme_state(d, ks.stg.variables.values(), wsd >= 0)
            mc_data[state][repr(self)] = wsd / ext_wsd


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
        for state in ks.stg.states:
            mc_data[state][repr(self)] = 1 if self.value else -1


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
        for state in ks.stg.states:
            mc_data[state][repr(self)] = min(mc_data[state][repr(self.left)], mc_data[state][repr(self.right)])


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
        for state in ks.stg.states:
            mc_data[state][repr(self)] = max(mc_data[state][repr(self.left)], mc_data[state][repr(self.right)])


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
        queue = set(ks.stg.states)
        while queue:
            state = queue.pop()
            succs = ks.stg.graph.successors(state)
            m = min(mc_data[s][repr(self.operand)] for s in succs)
            if mc_data[state][repr(self)] is None or m < mc_data[state][repr(self)]:
                mc_data[state][repr(self)] = m
                queue.update(ks.stg.graph.predecessors(state))


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
        queue = set(ks.stg.states)
        while queue:
            state = queue.pop()
            succs = ks.stg.graph.successors(state)
            m = min(mc_data[s][repr(self.operand)] for s in succs)
            if mc_data[state][repr(self)] is None or m > mc_data[state][repr(self)]:
                mc_data[state][repr(self)] = m
                queue.update(ks.stg.graph.predecessors(state))


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
        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            mc_data[state][repr(self)] = min(mc_data[s][repr(self.operand)] for s in succs)


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
        queue = set(ks.stg.states)
        while queue:
            state = queue.pop()
            succs = ks.stg.graph.successors(state)
            m = max(mc_data[s][repr(self.operand)] for s in succs)
            if mc_data[state][repr(self)] is None or m < mc_data[state][repr(self)]:
                mc_data[state][repr(self)] = m
                queue.update(ks.stg.graph.predecessors(state))


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
        queue = set(ks.stg.states)
        while queue:
            state = queue.pop()
            succs = ks.stg.graph.successors(state)
            m = max(mc_data[s][repr(self.operand)] for s in succs)
            if mc_data[state][repr(self)] is None or m > mc_data[state][repr(self)]:
                mc_data[state][repr(self)] = m
                queue.update(ks.stg.graph.predecessors(state))


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
        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            mc_data[state][repr(self)] = max(mc_data[s][repr(self.operand)] for s in succs)


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
        queue = set(ks.stg.states)
        for state in ks.stg.states:  # inicializujem pravou podformulou, horsie to uz nebude
            mc_data[state][repr(self)] = mc_data[state][repr(self.right)]
        while queue:
            state = queue.pop()
            succs = ks.stg.graph.successors(state)
            min_until_nexts = min([mc_data[s][repr(self)] for s in succs])  # najdem najhorsi path ktory zo mna vychadza
            sr, su = mc_data[state][repr(self.right)], mc_data[state][repr(self)]
            extend = min(sr, min_until_nexts)  # skusim ho predlzit o sucastny stav
            if extend > su:  # ak je predlzenie lepsie ako sucastna hodnota tak ju prepisem a notifikujem predchodcov
                mc_data[state][repr(self)] = extend
                queue.update(ks.stg.graph.predecessors(state))


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
        queue = set(ks.stg.states)
        for state in ks.stg.states:  # inicializujem pravou podformulou, horsie to uz nebude
            mc_data[state][repr(self)] = mc_data[state][repr(self.right)]
        while queue:
            state = queue.pop()
            succs = ks.stg.graph.successors(state)
            max_until_nexts = max([mc_data[s][repr(self)] for s in succs]) # najdem najlepsi path ktory zo mna vychadza
            sr, su = mc_data[state][repr(self.right)], mc_data[state][repr(self)]
            extend = min(sr, max_until_nexts)  # skusim ho predlzit o sucastny stav
            if extend > su:  # ak je predlzenie lepsie ako sucastna hodnota tak ju prepisem a notifikujem predchodcov
                mc_data[state][repr(self)] = extend
                queue.update(ks.stg.graph.predecessors(state))


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
        ag = AG(self.left)
        au = AU(self.left, self.right)
        for state in ks.stg.states:  # pre eu netreba, tam sa nastavi right aj tak
            mc_data[state][repr(ag)] = None

        ag.evaluate(ks, mc_data)
        au.evaluate(ks, mc_data)
        for state in ks.stg.states:  # nastavim maximom z tych dvoch
            mc_data[state][repr(self)] = max(mc_data[state][repr(ag)], mc_data[state][repr(au)])


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
        eg = EG(self.left)
        eu = EU(self.left, self.right)
        for state in ks.stg.states:  # pre eu netreba, tam sa nastavi right aj tak
            mc_data[state][repr(eg)] = None

        eg.evaluate(ks, mc_data)
        eu.evaluate(ks, mc_data)
        for state in ks.stg.states:  # nastavim maximom z tych dvoch
            mc_data[state][repr(self)] = max(mc_data[state][repr(eg)], mc_data[state][repr(eu)])


