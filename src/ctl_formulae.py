from abc import ABC, abstractmethod
from typing import List
from itertools import product
from src.quantitative_ctl import KripkeStructure
from src.satisfaction_degree import weighted_distance, find_extreme_state, get_border_states
from src.custom_types import SubspaceType, QuantLabelingFnType, MaxActivitiesType
from src.priority_queue import MinPriorityQueue, MaxPriorityQueue


class StateFormula(ABC):
    """
    Abstract base class representing a state CTL formula.

    A state formula defines logical conditions that hold in particular states
    of a Kripke structure. This class provides an interface for eliminating
    negation, retrieving subformulae, and evaluating the formula in a given
    Kripke structure.
    """

    @abstractmethod
    def eliminate_negation(self) -> 'StateFormula':
        """
        Eliminates negation from the formula, returning an equivalent negation-free formula.

        @return StateFormula: A transformed version of the formula without negations.
        """
        pass

    @abstractmethod
    def get_subformulae(self) -> List['StateFormula']:
        """
        Retrieves a list of subformulae contained within this formula.
        Important: The order in list ensures that all the subformulas of any formula are listed before.
        Especially, this means that when evaluating a formula, all of its subformulas have already been evaluated.

        @return A list of subformulae, where each element is an instance of StateFormula.
        """
        pass

    @abstractmethod
    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        """
        Evaluates the formula within the given Kripke structure.

        @param ks: The Kripke structure over which the formula is evaluated.
        @param formulae_evaluations: A data structure storing the evaluation results for states.
        @return None: The function modifies formulae_evaluations in place.
        """
        pass



class AtomicFormula(StateFormula):
    """
    Abstract base class for atomic formulas in CTL.

    Atomic formulas define constraints over states in a Kripke structure.
    """

    @abstractmethod
    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        """
        Computes the domain of validity for the atomic formula.

        @param max_activities: The maximum possible values for each variable.
        @return: Updated domain of validity.
        """
        pass

    def get_subformulae(self) -> List['StateFormula']:
        """
        Returns the subformulae of the atomic formula.

        Since atomic formulas are indivisible, they return themselves.

        @return: List containing only this formula.
        """
        return [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        """
        Evaluates the atomic formula in a given Kripke structure.

        @param ks: The Kripke structure to evaluate against.
        @param formulae_evaluations: A mapping of states to formula evaluations.
        """
        dov = self.compute_dov(ks.stg.variables)
        dov_complement = self.compute_dov_complement(dov, ks.stg.variables)
        border = get_border_states(dov, list(ks.stg.variables.values()))
        max_depth = find_extreme_state(dov, border, list(ks.stg.variables.values()))
        max_dist = find_extreme_state(dov_complement.union(border), border, list(ks.stg.variables.values()))
        for state in ks.stg.states:
            wd = weighted_distance(state, border, list(ks.stg.variables.values()))
            print(state, wd)
            if state in dov:
                formulae_evaluations[state][repr(self)] = wd / max_depth if max_depth > 0 else 0
            else:
                formulae_evaluations[state][repr(self)] = -wd / max_dist if max_depth > 0 else 0

    @staticmethod
    def compute_dov_complement(dov, max_activities) -> SubspaceType:
        """Returns the complement of the given set of states within the valid space."""
        variables = list(max_activities.keys())  # Ensure correct order
        full_space = set(product(*(range(max_activities[var] + 1) for var in variables)))
        return full_space - dov

    @abstractmethod
    def negate(self):
        pass


class AtomicProposition(AtomicFormula):
    def __init__(self, variable: str, operator: str, value: int) -> None:
        self.variable = variable
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f"({self.variable} {self.operator} {self.value})"

    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        max_val = max_activities[self.variable]
        if self.operator == ">=":
            valid_values = range(self.value, max_val + 1)
        else:  # self.operator == "<="
            valid_values = range(0, self.value + 1)
        domains = []
        for var in max_activities.keys():
            domains.append(valid_values if var == self.variable else range(0, max_activities[var] + 1))
        return set(product(*domains))

    def eliminate_negation(self) -> 'AtomicFormula':
        return self

    def negate(self):
        if self.operator == ">=":
            return AtomicProposition(self.variable, "<=", self.value - 1)
        elif self.operator == "<=":
            return AtomicProposition(self.variable, ">=", self.value + 1)


class Negation(AtomicFormula):
    def __init__(self, operand: AtomicFormula) -> None:
        self.operand = operand

    def __repr__(self) -> str:
        return f"!{repr(self.operand)}"

    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        raise NotImplementedError("Negation must be eliminated before calling yield_dov.")

    def eliminate_negation(self) -> AtomicFormula:
        if isinstance(self.operand, Negation):
            return self.operand.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        raise NotImplementedError("Negation must be eliminated before calling get_subformulae.")

    def negate(self):
        return self.operand.negate()


class Union(AtomicFormula):
    def __init__(self, left: AtomicFormula, right: AtomicFormula) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} | {repr(self.right)})"

    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        left_dov = self.left.compute_dov(max_activities)
        right_dov = self.right.compute_dov(max_activities)
        return left_dov.union(right_dov)

    def eliminate_negation(self) -> AtomicFormula:
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def negate(self):
        return Intersection(Negation(self.left), Negation(self.right))


class Intersection(AtomicFormula):
    def __init__(self, left: AtomicFormula, right: AtomicFormula) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} & {repr(self.right)})"

    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        left_dov = self.left.compute_dov(max_activities)
        right_dov = self.right.compute_dov(max_activities)
        return left_dov.intersection(right_dov)

    def eliminate_negation(self) -> AtomicFormula:
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def negate(self):
        return Union(Negation(self.left), Negation(self.right))


class Boolean(StateFormula):
    def __init__(self, value: bool):
        self.value = value

    def __repr__(self) -> str:
        return str(self.value)

    def eliminate_negation(self) -> 'StateFormula':
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = 1 if self.value else -1


class Conjunction(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} && {repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = min(formulae_evaluations[state][repr(self.left)], formulae_evaluations[state][repr(self.right)])


class Disjunction(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"({repr(self.left)} || {repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = max(formulae_evaluations[state][repr(self.left)], formulae_evaluations[state][repr(self.right)])


class AG(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"AG ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.operand, Negation):
            self.operand = self.operand.negate()
        self.operand = self.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        queue = MinPriorityQueue()
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = formulae_evaluations[state][repr(self.operand)]
            predcs = ks.stg.graph.predecessors(state)
            for p in predcs:
                queue.decrease_priority(p, formulae_evaluations[state][repr(self.operand)])

        while queue.heap:
            state, _ = queue.extract_min()
            succs = ks.stg.graph.successors(state)
            min_value = min([formulae_evaluations[s][repr(self.operand)] for s in succs])  # all needs minimal value of operand
            # if state has no value yet or propagated minimal value is smaller than actual best, replace it and notify predecessors
            if min_value < formulae_evaluations[state][repr(self)]:
                formulae_evaluations[state][repr(self)] = min_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.decrease_priority(p, formulae_evaluations[state][repr(self.operand)])


class EG(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"EG ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.operand, Negation):
            self.operand = self.operand.negate()
        self.operand = self.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        queue = MinPriorityQueue()
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = formulae_evaluations[state][repr(self.operand)]
            predcs = ks.stg.graph.predecessors(state)
            for p in predcs:
                queue.decrease_priority(p, formulae_evaluations[state][repr(self.operand)])

        while queue.heap:
            state, _ = queue.extract_min()
            succs = ks.stg.graph.successors(state)
            max_value = max([formulae_evaluations[s][repr(self.operand)] for s in succs])  # exists needs maximal value of operand
            # if state has no value yet or propagated maximal value is smaller than actual best, replace it and notify predecessors
            if max_value < formulae_evaluations[state][repr(self)]:
                formulae_evaluations[state][repr(self)] = max_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.decrease_priority(p, formulae_evaluations[state][repr(self.operand)])


class AF(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"AF ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.operand, Negation):
            self.operand = self.operand.negate()
        self.operand = self.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = formulae_evaluations[state][repr(self.operand)]
            predcs = ks.stg.graph.predecessors(state)
            for p in predcs:
                queue.increase_priority(p, formulae_evaluations[state][repr(self.operand)])

        while queue.heap:
            state, _ = queue.extract_max()
            succs = list(ks.stg.graph.successors(state))
            min_value = min([formulae_evaluations[s][repr(self.operand)] for s in succs])  # all needs minimal value of operand
            # if state has no value yet or propagated minimal value is greater than actual best, replace it and notify predecessors
            if min_value > formulae_evaluations[state][repr(self)]:
                formulae_evaluations[state][repr(self)] = min_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, formulae_evaluations[state][repr(self.operand)])


class EF(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"EF ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.operand, Negation):
            self.operand = self.operand.negate()
        self.operand = self.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = formulae_evaluations[state][repr(self.operand)]
            predcs = ks.stg.graph.predecessors(state)
            for p in predcs:
                queue.increase_priority(p, formulae_evaluations[state][repr(self.operand)])

        while queue.heap:
            state, _ = queue.extract_max()
            succs = ks.stg.graph.successors(state)
            max_value = max([formulae_evaluations[s][repr(self.operand)] for s in succs])  # exists needs maximal value of operand
            # if state has no value yet or propagated maximal value is greater than actual best, replace it and notify predecessors
            if max_value > formulae_evaluations[state][repr(self)]:
                formulae_evaluations[state][repr(self)] = max_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, formulae_evaluations[state][repr(self.operand)])


class AX(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"AX ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.operand, Negation):
            self.operand = self.operand.negate()
        self.operand = self.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            formulae_evaluations[state][repr(self)] = min([formulae_evaluations[s][repr(self.operand)] for s in succs])


class EX(StateFormula):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def __repr__(self) -> str:
        return f"EX ({repr(self.operand)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.operand, Negation):
            self.operand = self.operand.negate()
        self.operand = self.operand.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            formulae_evaluations[state][repr(self)] = max([formulae_evaluations[s][repr(self.operand)] for s in succs])


class AU(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"A ({repr(self.left)}) U ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:  # initialize the computation with the right operand value in each state
            formulae_evaluations[state][repr(self)] = formulae_evaluations[state][repr(self.right)]
            predcs = ks.stg.graph.predecessors(state)
            for p in predcs:
                queue.increase_priority(p, formulae_evaluations[state][repr(self.right)])

        while queue.heap:
            state, _ = queue.extract_max()
            succs = ks.stg.graph.successors(state)
            min_until_nexts = min([formulae_evaluations[s][repr(self)] for s in succs])  # all takes minimal value of the whole Until from successors
            left_self, until_self = formulae_evaluations[state][repr(self.left)], formulae_evaluations[state][repr(self)]
            extend = min(left_self, min_until_nexts)   # tries to extend the prefix with the current left
            if extend > until_self:  # compare the extended prefix with actual value of until, if extension is better, then update
                formulae_evaluations[state][repr(self)] = extend
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, extend)


class EU(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"E ({repr(self.left)}) U ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:  # initialize the computation with the right operand value in each state
            formulae_evaluations[state][repr(self)] = formulae_evaluations[state][repr(self.right)]
            predcs = ks.stg.graph.predecessors(state)
            for p in predcs:
                queue.increase_priority(p, formulae_evaluations[state][repr(self.right)])  # not sure

        while queue.heap:
            state, _ = queue.extract_max()
            succs = ks.stg.graph.successors(state)
            max_until_nexts = max([formulae_evaluations[s][repr(self)] for s in succs])  # exists takes minimal value of the whole Until from successors
            left_self, until_self = formulae_evaluations[state][repr(self.left)], formulae_evaluations[state][repr(self)]
            extend = min(left_self, max_until_nexts)  # tries to extend the prefix with the current left
            if extend > until_self:  # compare the extended prefix with actual value of until, if extension is better, then update
                formulae_evaluations[state][repr(self)] = extend
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, extend)


class AW(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"A ({repr(self.left)}) W ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        """The problem here is that you cannot optimize between AG and AU online because you have no guarantee on AG
        until it finally converges. It can happen that you overwrite the best AU by best AG at some point, but later
        you find out that the AG is actually very poor. But the information about best AU is already lost.
        The solution is to optimize both options separately and finally to optimize between them in each state."""

        ag = AG(self.left)
        au = AU(self.left, self.right)
        ag.evaluate(ks, formulae_evaluations)
        au.evaluate(ks, formulae_evaluations)
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = max(formulae_evaluations[state][repr(ag)], formulae_evaluations[state][repr(au)])


class EW(StateFormula):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"E ({repr(self.left)}) W ({repr(self.right)})"

    def eliminate_negation(self) -> 'StateFormula':
        if isinstance(self.left, Negation):
            self.left = self.left.negate()
        if isinstance(self.right, Negation):
            self.right = self.right.negate()
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def evaluate(self, ks: KripkeStructure, formulae_evaluations: QuantLabelingFnType) -> None:
        """The problem here is that you cannot optimize between EG and EU online because you have no guarantee on EG
        until it finally converges. It can happen that you overwrite the best EU by best EG at some point, but later
        you find out that the EG is actually very poor. But the information about best EU is already lost.
        The solution is to optimize both options separately and finally to optimize between them in each state."""

        eg = EG(self.left)
        eu = EU(self.left, self.right)

        eg.evaluate(ks, formulae_evaluations)
        eu.evaluate(ks, formulae_evaluations)
        for state in ks.stg.states:
            formulae_evaluations[state][repr(self)] = max(formulae_evaluations[state][repr(eg)], formulae_evaluations[state][repr(eu)])
