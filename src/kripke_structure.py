from typing import Optional, List, Set
from src.custom_types import StateType, QuantLabelingFnType


class KripkeStructure:
    """
    Represents a Kripke Structure used for model checking.

    A Kripke structure consists of a state transition graph (STG) and a set of initial states.
    If no initial states are provided, all states in the transition graph are considered initial.

    @param stg: The state transition graph representing the structure.
    @param labels List of labels of subformulae of the verified formula.
    @param init_states: A list of initial states.
    """
    def __init__(self, stg, labels: List[str], init_states: List[StateType]):
        self.stg = stg
        self.quantitative_labeling = self._init_quantitative_labeling(self._remove_duplicate_labels(labels))
        self.init_states = init_states

    @staticmethod
    def _remove_duplicate_labels(labels):
        """
        Removes repeating subformulas to increase efficiency

        @param labels list of original subformula labels
        @return list of unique subformulas' labels
        """
        seen = set()
        return [x for x in labels if not (x in seen or seen.add(x))]

    def _init_quantitative_labeling(self, labels: List[str]) -> QuantLabelingFnType:
        """
        Initializes a dictionary to store the evaluation results of formulas for each state in the Kripke structure.

        The dictionary structure is as follows:
        - Each state in the Kripke structure maps to another dictionary.
        - This nested dictionary maps each formula label to its evaluation result (initially set to None).

        @param labels: A list of string representations of formulae to be evaluated.
        @return: A dictionary mapping each state to a dictionary of formula evaluations (initially None).
        """
        return {state: {label: None for label in labels} for state in self.stg.states}

    def model_check(self, subformulae) -> QuantLabelingFnType:
        """
        Performs model checking for a given Kripke structure and subformulae of verified formula.
        Evaluate each subformula iteratively in the order provided.

        @return: A mapping of states to their evaluation results for each subformula.
        """
        for sf in subformulae:
            sf.evaluate(self)
            print("Done ", sf)
        return self.quantitative_labeling

