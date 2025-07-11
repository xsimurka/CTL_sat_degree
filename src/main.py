from sys import argv
from json import load
from itertools import product
from math import inf
from multivalued_grn import StateTransitionGraph, MvGRNParser
from lark_ctl_parser import parse_formula
from kripke_structure import KripkeStructure
from custom_types import StateType, QuantLabelingFnType, MaxActivitiesType
from typing import List, Dict, Set
from ctl_formulae import StateFormula


def main():
    """
    Main function that loads data, parses formula, validates initial states, generates states,
    builds Kripke structure, performs model checking, and prints results.
    """
    if len(argv) != 2:
        print("Script expects exactly one argument - path to json file.")
        exit(1)

    with open(argv[1], 'r') as file:
        json_data = load(file)

    # Formula
    formula_data = json_data.get("formula")
    parsed_formula = parse_formula(formula_data)
    positive_formula = parsed_formula.eliminate_negation()
    subformulae = positive_formula.get_subformulae()
    labels = [repr(sf) for sf in subformulae]

    # Multivalued Gene Regulatory Network
    network_data = json_data.get("network")
    mvgrn = MvGRNParser(network_data).parse()
    stg = StateTransitionGraph(mvgrn)

    # Initial states
    init_states_data = json_data.get("init_states")
    validate_initial_states(init_states_data, mvgrn.variables)
    initial_states = generate_initial_states(init_states_data, network_data.get("variables"))

    # Satisfaction degree computation
    ks = KripkeStructure(stg, labels, initial_states)
    formulae_evaluations = ks.evaluate(subformulae)
    format_result(formulae_evaluations, ks.init_states, positive_formula)


def validate_initial_states(initial_states: List[Dict[str, List[int]]], variables: MaxActivitiesType):
    """
    Validates whether all constraints in initial_states lie within the allowed range [0, max_activity_value].

    @param initial_states: Dictionary of initial state constraints { variable_name: value }
    @param variables: Dictionary of variables and their corresponding maximum activity values
    @raises ValueError: If any value is out of bounds or the variable doesn't exist in variables.
    """
    for region in initial_states:
        for var, values in region.items():
            if var not in variables:
                raise ValueError(f"Variable '{var}' not found in the network.")

            max_value = variables[var]
            if any(not 0 <= v <= max_value for v in values):
                raise ValueError(
                    f"Some value from {values} for variable '{var}' is out of bounds. Allowed range is [0, {max_value}]."
                )


def generate_initial_states(initial_states: List[Dict[str, List[int]]], variables: MaxActivitiesType) -> List[StateType]:
    """
    Generates all possible initial states based on given constraints and variable domains.

    @param initial_states: List of dictionaries containing constraints on initial state values { variable_name: list of admissible values }
    @param variables: Dictionary of variables with their maximum values { variable_name: max_value }
    @return: List of all possible initial states as tuples
    """
    if not initial_states:
        return list(product(*(range(max_act + 1) for max_act in variables.values())))

    ordered_variables = list(variables.keys())
    result: Set = set()
    for region in initial_states:
        domains = []
        for var in ordered_variables:
            domains.append(set(region.get(var, range(variables[var] + 1))))
        result.update(product(*domains))

    return list(result)


def format_result(quantitative_labeling: QuantLabelingFnType, initial_states: List[StateType],
                  formula: StateFormula) -> None:
    """
    Formats and prints the results of the formula evaluation on initial states.
    Namely prints: worst and best values along with an arbitrary state,
    average satisfaction degree value among the initial states.

    @param quantitative_labeling: Quantitative labeling function
    @param initial_states: List of initial states
    @param formula: The formula being evaluated
    """
    minimum, maximum, cumulative = inf, -inf, 0
    min_state, max_state = None, None
    for state in initial_states:
        value = quantitative_labeling[state][repr(formula)]
        if value < minimum:
            min_state = state
            minimum = value
        if value > maximum:
            max_state = state
            maximum = value
        cumulative += value

    print("Formula:", repr(formula))
    print("Worst value", minimum, "in state", min_state)
    print("Best value", maximum, "in state", max_state)
    print("Average value among initial states:", cumulative / len(initial_states))


if __name__ == "__main__":
    main()
