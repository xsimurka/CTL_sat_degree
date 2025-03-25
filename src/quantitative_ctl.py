from typing import Optional, List, Dict
from src.custom_types import StateType, FormulaEvaluationType


class KripkeStructure:
    """
    Represents a Kripke Structure used for model checking.

    @param stg: The state transition graph representing the structure.
    @param init_states: A list of initial states. If None, defaults to all states in the transition graph.
    """

    def __init__(self, stg, init_states: Optional[List[StateType]]):
        self.stg = stg
        self.init_states = init_states if init_states is not None else stg.states


def model_check(ks: KripkeStructure, formula) -> FormulaEvaluationType:
    """
    Performs model checking for a given Kripke structure and formula.

    @param ks: The Kripke structure on which to perform model checking.
    @param formula: The logical formula to be evaluated within the structure.
    @return: A mapping of states to their evaluation results for each subformula.
    """
    subformulae = formula.get_subformulae()
    formulae_evaluations = init_formulae_evaluations(ks, [repr(sf) for sf in subformulae])
    for sf in subformulae:
        sf.evaluate(ks, formulae_evaluations)

    return formulae_evaluations


def init_formulae_evaluations(ks: KripkeStructure, labels: List[str]) -> Dict[StateType, Dict[str, Optional[bool]]]:
    """
    Initializes a dictionary to store the evaluation of formulas for each state.

    @param ks: The Kripke structure containing states to initialize evaluations for.
    @param labels: A list of string representations of formulae to be evaluated.
    @return: A dictionary mapping each state to a dictionary of formula evaluations (initially None).
    """
    formulae_evaluations = {}
    for state in ks.stg.states:
        formulae_evaluations[state] = {label: None for label in labels}

    return formulae_evaluations
