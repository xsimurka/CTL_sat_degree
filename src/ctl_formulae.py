from abc import ABC, abstractmethod
from math import inf
from typing import List
from itertools import product
from kripke_structure import KripkeStructure
from weighted_distance import weighted_distance, find_extreme_depth, get_border_states
from custom_types import SubspaceType, MaxActivitiesType
from priority_queue import MinPriorityQueue, MaxPriorityQueue


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
        Transforms the formula into an equivalent form without explicit negations.

        This method recursively replaces negated formulas with their logically equivalent
        forms using De Morgan’s laws, eliminating the use of the Negation class entirely.
        The returned formula is guaranteed not to contain any instances of Negation.

        @return StateFormula: A logically equivalent formula with all negations eliminated.
        """
        ...

    @abstractmethod
    def get_subformulae(self) -> List['StateFormula']:
        """
        Retrieves a list of subformulae contained within this formula.
        Important: The order in list ensures that all the subformulas of any formula are listed before.
        Especially, this means that when evaluating a formula, all of its subformulas have already been evaluated.

        @return A list of subformulae, where each element is an instance of StateFormula.
        """
        ...

    @abstractmethod
    def evaluate(self, ks: KripkeStructure) -> None:
        """
        Evaluates the formula within the given Kripke structure.

        @param ks: The Kripke structure over which the formula is evaluated.
        @return None: The function modifies Kripke structure in place.
        """
        ...


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
        ...

    @abstractmethod
    def negate(self) -> 'AtomicFormula':
        """
        Returns the logical negation of the atomic formula.

        This method recursively constructs a new formula that represents the logical negation
        of the current one.

        @return AtomicFormula: A formula logically equivalent to the negation of the current one.
        """
        ...

    def get_subformulae(self) -> List[StateFormula]:
        """
        Returns the subformulae of the atomic formula. Since atomic formulas are indivisible, they return themselves.

        @return: List containing only this formula.
        """
        return [self]

    def evaluate(self, ks: KripkeStructure) -> None:
        """
        Evaluates the atomic formula in a given Kripke structure. Updates Kripke structure.

        @param ks: The Kripke structure to evaluate against.
        """
        dov = self.compute_dov(ks.stg.variables)
        co_dov = self.compute_dov_complement(dov, ks.stg.variables)
        dov_b, co_dov_b = get_border_states(dov, list(ks.stg.variables.values()))
        max_dov_depth = find_extreme_depth(dov, co_dov_b, list(ks.stg.variables.values()))
        max_co_dov_depth = find_extreme_depth(co_dov, dov_b, list(ks.stg.variables.values()))
        for state in ks.stg.states:
            if state in dov:
                wd = weighted_distance(state, co_dov_b, list(ks.stg.variables.values()))
                ks.quantitative_labeling[state][repr(self)] = wd / max_dov_depth if max_dov_depth != inf else 1
            else:
                wd = weighted_distance(state, dov_b, list(ks.stg.variables.values()))
                ks.quantitative_labeling[state][repr(self)] = -wd / max_co_dov_depth if max_co_dov_depth != inf else -1

    @staticmethod
    def compute_dov_complement(dov, max_activities) -> SubspaceType:
        """Returns the complement of the given set of states within the valid space."""
        variables = list(max_activities.keys())  # Ensure correct order
        full_space = set(product(*(range(max_activities[var] + 1) for var in variables)))
        return full_space - dov


class AtomicProposition(AtomicFormula):
    def __init__(self, variable: str, operator: str, value: int) -> None:
        self.variable = variable
        self.operator = operator
        self.value = value

    def __repr__(self) -> str:
        return f"{self.variable} {self.operator} {self.value}"

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

    def eliminate_negation(self) -> StateFormula:
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
        negated = self.operand.negate().eliminate_negation()
        return negated

    def get_subformulae(self) -> List['StateFormula']:
        raise NotImplementedError("Negation must be eliminated before calling get_subformulae.")

    def negate(self):
        return self.operand


class Union(AtomicFormula):
    def __init__(self, left: AtomicFormula, right: AtomicFormula) -> None:
        self.left = left
        self.right = right

    def __repr__(self) -> str:
        return f"{repr(self.left)} | {repr(self.right)}"

    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        left_dov = self.left.compute_dov(max_activities)
        right_dov = self.right.compute_dov(max_activities)
        return left_dov.union(right_dov)

    def eliminate_negation(self) -> AtomicFormula:
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
        return f"{repr(self.left)} & {repr(self.right)}"

    def compute_dov(self, max_activities: MaxActivitiesType) -> SubspaceType:
        left_dov = self.left.compute_dov(max_activities)
        right_dov = self.right.compute_dov(max_activities)
        return left_dov.intersection(right_dov)

    def eliminate_negation(self) -> AtomicFormula:
        self.left = self.left.eliminate_negation()
        self.right = self.right.eliminate_negation()
        return self

    def negate(self):
        return Union(Negation(self.left), Negation(self.right))


class UnaryOperator(StateFormula, ABC):
    def __init__(self, operand: StateFormula):
        self.operand = operand

    def get_subformulae(self) -> List['StateFormula']:
        return self.operand.get_subformulae() + [self]

    def eliminate_negation(self) -> 'StateFormula':
        self.operand = self.operand.eliminate_negation()
        return self


class AG(UnaryOperator):
    def __repr__(self) -> str:
        return f"AG ({repr(self.operand)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        queue = MinPriorityQueue()
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = ks.quantitative_labeling[state][repr(self.operand)]

        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            priority = min([ks.quantitative_labeling[s][repr(self)] for s in succs])
            queue.decrease_priority(state, priority)

        while queue.heap:
            state, _ = queue.extract_min()
            succs = ks.stg.graph.successors(state)
            min_value = min(
                [ks.quantitative_labeling[s][repr(self)] for s in succs])  # all needs minimal value of operand
            # if state has no value yet or propagated minimal value is smaller than actual best, replace it and notify predecessors
            if min_value < ks.quantitative_labeling[state][repr(self)]:
                ks.quantitative_labeling[state][repr(self)] = min_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.decrease_priority(p, min_value)


class EG(UnaryOperator):
    def __repr__(self) -> str:
        return f"EG ({repr(self.operand)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        queue = MinPriorityQueue()
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = ks.quantitative_labeling[state][repr(self.operand)]

        for state in ks.stg.states:
            succs = list(ks.stg.graph.successors(state))
            priority = min([ks.quantitative_labeling[s][repr(self)] for s in succs])
            queue.decrease_priority(state, priority)

        while queue.heap:
            state, _ = queue.extract_min()
            succs = ks.stg.graph.successors(state)
            max_value = max(
                [ks.quantitative_labeling[s][repr(self)] for s in succs])  # exists needs maximal value of operand
            # if state has no value yet or propagated maximal value is smaller than actual best, replace it and notify predecessors
            if max_value < ks.quantitative_labeling[state][repr(self)]:
                ks.quantitative_labeling[state][repr(self)] = max_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.decrease_priority(p, max_value)


class AF(UnaryOperator):
    def __repr__(self) -> str:
        return f"AF ({repr(self.operand)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = ks.quantitative_labeling[state][repr(self.operand)]

        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            priority = max([ks.quantitative_labeling[s][repr(self)] for s in succs])
            queue.increase_priority(state, priority)

        while queue.heap:
            state, _ = queue.extract_max()
            succs = list(ks.stg.graph.successors(state))
            min_value = min(
                [ks.quantitative_labeling[s][repr(self)] for s in succs])  # all needs minimal value of operand
            # if state has no value yet or propagated minimal value is greater than actual best, replace it and notify predecessors
            if min_value > ks.quantitative_labeling[state][repr(self)]:
                ks.quantitative_labeling[state][repr(self)] = min_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, min_value)


class EF(UnaryOperator):
    def __repr__(self) -> str:
        return f"EF ({repr(self.operand)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = ks.quantitative_labeling[state][repr(self.operand)]

        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            priority = max([ks.quantitative_labeling[s][repr(self)] for s in succs])
            queue.increase_priority(state, priority)

        while queue.heap:
            state, _ = queue.extract_max()
            succs = ks.stg.graph.successors(state)
            max_value = max(
                [ks.quantitative_labeling[s][repr(self)] for s in succs])  # exists needs maximal value of operand
            # if state has no value yet or propagated maximal value is greater than actual best, replace it and notify predecessors
            if max_value > ks.quantitative_labeling[state][repr(self)]:
                ks.quantitative_labeling[state][repr(self)] = max_value  # replace the original value
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, max_value)


class AX(UnaryOperator):
    def __repr__(self) -> str:
        return f"AX ({repr(self.operand)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            ks.quantitative_labeling[state][repr(self)] = min(
                [ks.quantitative_labeling[s][repr(self.operand)] for s in succs])


class EX(UnaryOperator):
    def __repr__(self) -> str:
        return f"EX ({repr(self.operand)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            ks.quantitative_labeling[state][repr(self)] = max(
                [ks.quantitative_labeling[s][repr(self.operand)] for s in succs])


class BinaryOperator(StateFormula, ABC):
    def __init__(self, left: StateFormula, right: StateFormula):
        self.left = left
        self.right = right

    def get_subformulae(self) -> List['StateFormula']:
        sub_left = self.left.get_subformulae()
        sub_right = self.right.get_subformulae()
        return sub_left + sub_right + [self]

    def eliminate_negation(self) -> 'StateFormula':
        self.right = self.right.eliminate_negation()
        self.left = self.left.eliminate_negation()
        return self


class Conjunction(BinaryOperator):
    def __repr__(self) -> str:
        return f"{repr(self.left)} && {repr(self.right)}"

    def evaluate(self, ks: KripkeStructure) -> None:
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = min(ks.quantitative_labeling[state][repr(self.left)],
                                                              ks.quantitative_labeling[state][repr(self.right)])


class Disjunction(BinaryOperator):
    def __repr__(self) -> str:
        return f"{repr(self.left)} || {repr(self.right)}"

    def evaluate(self, ks: KripkeStructure) -> None:
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = max(ks.quantitative_labeling[state][repr(self.left)],
                                                              ks.quantitative_labeling[state][repr(self.right)])


class AU(BinaryOperator):
    def __repr__(self) -> str:
        return f"A ({repr(self.left)}) U ({repr(self.right)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:  # initialize the computation with the right operand value in each state
            ks.quantitative_labeling[state][repr(self)] = ks.quantitative_labeling[state][repr(self.right)]

        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            priority = max([ks.quantitative_labeling[s][repr(self)] for s in succs])
            queue.increase_priority(state, priority)

        while queue.heap:
            state, _ = queue.extract_max()
            succs = ks.stg.graph.successors(state)
            min_until_nexts = min([ks.quantitative_labeling[s][repr(self)] for s in
                                   succs])  # all takes minimal value of the whole Until from successors
            left_self, until_self = ks.quantitative_labeling[state][repr(self.left)], ks.quantitative_labeling[state][
                repr(self)]
            extend = min(left_self, min_until_nexts)  # tries to extend the prefix with the current left
            if extend > until_self:  # compare the extended prefix with actual value of until, if extension is better, then update
                ks.quantitative_labeling[state][repr(self)] = extend
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, extend)


class EU(BinaryOperator):
    def __repr__(self) -> str:
        return f"E ({repr(self.left)}) U ({repr(self.right)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        queue = MaxPriorityQueue()
        for state in ks.stg.states:  # initialize the computation with the right operand value in each state
            ks.quantitative_labeling[state][repr(self)] = ks.quantitative_labeling[state][repr(self.right)]

        for state in ks.stg.states:
            succs = ks.stg.graph.successors(state)
            priority = max([ks.quantitative_labeling[s][repr(self)] for s in succs])
            queue.increase_priority(state, priority)

        while queue.heap:
            state, _ = queue.extract_max()
            succs = ks.stg.graph.successors(state)
            max_until_nexts = max([ks.quantitative_labeling[s][repr(self)] for s in
                                   succs])  # exists takes minimal value of the whole Until from successors
            left_self, until_self = ks.quantitative_labeling[state][repr(self.left)], ks.quantitative_labeling[state][
                repr(self)]
            extend = min(left_self, max_until_nexts)  # tries to extend the prefix with the current left
            if extend > until_self:  # compare the extended prefix with actual value of until, if extension is better, then update
                ks.quantitative_labeling[state][repr(self)] = extend
                predcs = ks.stg.graph.predecessors(state)
                for p in predcs:
                    queue.increase_priority(p, extend)


class AW(BinaryOperator):
    def __repr__(self) -> str:
        return f"A ({repr(self.left)}) W ({repr(self.right)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        """The problem here is that you cannot optimize between AG and AU online because you have no guarantee on AG
        until it finally converges. It can happen that you overwrite the best AU by best AG at some point, but later
        you find out that the AG is actually very poor. But the information about best AU is already lost.
        The solution is to optimize both options separately and finally to optimize between them in each state."""

        ag = AG(self.left)
        au = AU(self.left, self.right)
        ag.evaluate(ks)
        au.evaluate(ks)
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = max(ks.quantitative_labeling[state][repr(ag)],
                                                              ks.quantitative_labeling[state][repr(au)])


class EW(BinaryOperator):
    def __repr__(self) -> str:
        return f"E ({repr(self.left)}) W ({repr(self.right)})"

    def evaluate(self, ks: KripkeStructure) -> None:
        """The problem here is that you cannot optimize between EG and EU online because you have no guarantee on EG
        until it finally converges. It can happen that you overwrite the best EU by best EG at some point, but later
        you find out that the EG is actually very poor. But the information about best EU is already lost.
        The solution is to optimize both options separately and finally to optimize between them in each state."""

        eg = EG(self.left)
        eu = EU(self.left, self.right)

        eg.evaluate(ks)
        eu.evaluate(ks)
        for state in ks.stg.states:
            ks.quantitative_labeling[state][repr(self)] = max(ks.quantitative_labeling[state][repr(eg)],
                                                              ks.quantitative_labeling[state][repr(eu)])
