from typing import Optional, List
from src.custom_types import StateType, QuantLabelingFnType


class KripkeStructure:
    """
    Represents a Kripke Structure used for model checking.

    A Kripke structure consists of a state transition graph (STG) and a set of initial states.
    If no initial states are provided, all states in the transition graph are considered initial.

    @param stg: The state transition graph representing the structure.
    @param init_states: A list of initial states. If None, defaults to all states in the transition graph.
    """

    def __init__(self, stg, init_states: Optional[List[StateType]] = None):
        self.stg = stg
        self.init_states = init_states if init_states is not None else stg.states


def model_check(ks: KripkeStructure, formula) -> QuantLabelingFnType:
    """
    Performs model checking for a given Kripke structure and logical formula.

    The algorithm follows these steps:
    1. Extract all subformulae from the given formula.
    2. Initialize a dictionary to store evaluation results for each state and subformula.
    3. Evaluate each subformula iteratively in the order provided.

    @param ks: The Kripke structure on which to perform model checking.
    @param formula: The logical formula to be evaluated within the structure.
    @return: A mapping of states to their evaluation results for each subformula.
    """
    subformulae = formula.get_subformulae()
    formulae_evaluations = init_formulae_evaluations(ks, [repr(sf) for sf in subformulae])

    for sf in subformulae:
        sf.evaluate(ks, formulae_evaluations)

    return formulae_evaluations


def init_formulae_evaluations(ks: KripkeStructure, labels: List[str]) -> QuantLabelingFnType:
    """
    Initializes a dictionary to store the evaluation results of formulas for each state in the Kripke structure.

    The dictionary structure is as follows:
    - Each state in the Kripke structure maps to another dictionary.
    - This nested dictionary maps each formula label to its evaluation result (initially set to None).

    @param ks: The Kripke structure containing states to initialize evaluations for.
    @param labels: A list of string representations of formulae to be evaluated.
    @return: A dictionary mapping each state to a dictionary of formula evaluations (initially None).
    """
    return {state: {label: None for label in labels} for state in ks.stg.states}
