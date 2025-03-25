import json
from math import inf
from src.multivalued_network import StateTransitionGraph, MvGRNParser
from src.lark_ctl_parser import parse_formula
from src.quantitative_ctl import model_check, KripkeStructure
from src.ctl_formulae import StateFormula
import itertools

json_string = '''
{
  "network": {
    "variables": {
      "gene1": 3,
      "gene2": 3,
      "gene3": 2,
      "gene4": 3
    },
    "regulations": [
      {
        "target": "gene1",
        "regulators": [
          { "variable": "gene2", "thresholds": [1, 2] },
          { "variable": "gene3", "thresholds": [1, 2] }
        ],
        "contexts": [
          { "intervals": [2, 1], "target_value": 0 },
          { "intervals": [1, 1], "target_value": 1 },
          { "intervals": [1, 2], "target_value": 2 },
          { "intervals": [2, 2], "target_value": 2 },
          { "intervals": ["*", "*"], "target_value": 2 }
        ]
      },
      {
        "target": "gene2",
        "regulators": [
          { "variable": "gene1", "thresholds": [1, 2] },
          { "variable": "gene4", "thresholds": [1] }
        ],
        "contexts": [
          { "intervals": [1, "*"], "target_value": 2 },
          { "intervals": [2, "*"], "target_value": 1 },
          { "intervals": ["*", 1], "target_value": 1 },
          { "intervals": ["*", 2], "target_value": 0 },
          { "intervals": [1, 1], "target_value": 2 },
          { "intervals": [2, 1], "target_value": 1 }
        ]
      },
      {
        "target": "gene3",
        "regulators": [
          { "variable": "gene1", "thresholds": [1, 2] },
          { "variable": "gene4", "thresholds": [2] }
        ],
        "contexts": [
          { "intervals": [1, "*"], "target_value": 0 },
          { "intervals": [2, "*"], "target_value": 2 },
          { "intervals": ["*", 2], "target_value": 1 },
          { "intervals": [3, 2], "target_value": 0 },
          { "intervals": ["*", 1], "target_value": 0 }
        ]
      },
      {
        "target": "gene4",
        "regulators": [
          { "variable": "gene2", "thresholds": [2] },
          { "variable": "gene3", "thresholds": [1] }
        ],
        "contexts": [
          { "intervals": [1, 1], "target_value": 2 },
          { "intervals": [2, 2], "target_value": 0 },
          { "intervals": ["*", "*"], "target_value": 1 }
        ]
      }
    ]
  },
  "formula": "AG (gene1 <= 3 && gene2 >= 1)",
  "initial_states": {
    "gene1": 1,
    "gene2": 2,
    "gene3": 0,
    "gene4": 1
  }
}
'''


def validate_initial_states(initial_states, mvgrn):
    """
    Validates whether all constraints in initial_states lie within the allowed range [0, max_activity_value].

    @param initial_states: Dictionary of initial state constraints { variable_name: value }
    @param mvgrn: Parsed MvGRN object
    @raises ValueError: If any value is out of bounds or the variable doesn't exist in mvgrn.
    """
    for var, value in initial_states.items():
        if var not in mvgrn.variables:
            raise ValueError(f"Variable '{var}' not found in the network.")

        max_value = mvgrn.variables[var]

        if not (0 <= value <= max_value):
            raise ValueError(
                f"Value {value} for variable '{var}' is out of bounds. Allowed range is [0, {max_value}]."
            )


def generate_initial_states(initial_states: dict, variables: dict):
    """
    Generates all possible initial states based on given constraints and variable domains.

    @param initial_states: Dictionary containing constraints on initial state values { variable_name: value }
    @param variables: Dictionary of variables with their maximum values { variable_name: max_value }
    @return: List of all possible initial states as tuples
    """
    ordered_variables = list(variables.keys())
    domains = []
    for var in ordered_variables:
        if var in initial_states:
            domains.append([initial_states[var]])
        else:
            domains.append(list(range(variables[var] + 1)))

    all_states = list(itertools.product(*domains))
    return all_states


def format_result(formulae_evaluations, initial_states, formula) -> None:
    """
    Formats and prints the results of the formula evaluation on initial states.

    @param formulae_evaluations: Dictionary mapping states to formula evaluations
    @param initial_states: List of initial states
    @param formula: The formula being evaluated
    """
    minimum, maximum, cumulative = inf, -inf, 0
    min_state, max_state = None, None
    for state in initial_states:
        value = formulae_evaluations[state][repr(formula)]
        if value < minimum:
            min_state = state
            minimum = value
        if value > maximum:
            max_state = state
            maximum = value
        cumulative += value

    print("Formula:", repr(formula))
    print("Best value", maximum, "in state", max_state)
    print("Best value", minimum, "in state", min_state)
    print("Average value among initial states:", cumulative / len(initial_states))


def main(json_file):
    """
    Main function to load data, parse formulas, validate states, generate states, build Kripke structure,
    perform model checking, and print results.

    @param json_file: Path to the JSON file containing input data
    """
    with open(json_file, 'r') as file:
        json_data = json.load(file)

    formula = json_data.get("formula")
    parsed_formula: StateFormula = parse_formula(formula)
    positive_formula: StateFormula = parsed_formula.eliminate_negation()
    initial_states = json_data.get("initial_states")
    network_data = json_data.get("network")
    mvgrn = MvGRNParser(network_data).parse()
    validate_initial_states(initial_states, mvgrn)
    stg = StateTransitionGraph(mvgrn)
    initial_states = generate_initial_states(json_data.get("initial_states"), json_data.get("network").get("variables"))
    ks = KripkeStructure(stg, initial_states)
    formulae_evaluations = model_check(ks, positive_formula)
    format_result(formulae_evaluations, initial_states, positive_formula)


if __name__ == "__main__":
    json_file = "path_to_your_json_file.json"  # Update this path to your JSON file
    main(json_file)
