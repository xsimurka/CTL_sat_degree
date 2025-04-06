import json
from math import inf
from src.multivalued_network import StateTransitionGraph, MvGRNParser
from src.lark_ctl_parser import parse_formula
from src.quantitative_ctl import model_check, KripkeStructure
import itertools
import networkx as nx

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
    print("Worst value", minimum, "in state", min_state)
    print("Average value among initial states:", cumulative / len(initial_states))


def main2(json_file):
    """
    Main function to load data, parse formulas, validate states, generate states, build Kripke structure,
    perform model checking, and print results.

    @param json_file: Path to the JSON file containing input data
    """
    # with open(json_file, 'r') as file:
    #     json_data = json.load(file)

    # formula = json_data.get("formula")
    # parsed_formula: StateFormula = parse_formula(formula)
    # positive_formula: StateFormula = parsed_formula.eliminate_negation()
    # initial_states = json_data.get("initial_states")
    # network_data = json_data.get("network")
    # mvgrn = MvGRNParser(network_data).parse()
    # validate_initial_states(initial_states, mvgrn)
    # stg = StateTransitionGraph(mvgrn)
    variables = {
        "x": 5,  # Activity levels: 0, 1, 2
        "y": 4,  # Activity levels: 0, 1, 2, 3
    }

    # Define regulations (simplified for generating transitions)
    regulations = {
        "x": {"y": [1, 3]},  # A is regulated by B's levels
        "y": {"x": [1]},  # B is regulated by A and C
    }

    # Generate all possible states
    all_states = list(itertools.product(*[range(v + 1) for v in variables.values()]))

    # Create a directed graph
    G = nx.DiGraph()
    G.add_nodes_from(all_states)

    # Function to generate transitions based on regulations
    def generate_successors(state):
        successors = []
        state_dict = {gene: state[i] for i, gene in enumerate(variables)}

        for gene, regs in regulations.items():
            idx = list(variables.keys()).index(gene)
            current_value = state[idx]

            for regulator, thresholds in regs.items():
                reg_idx = list(variables.keys()).index(regulator)
                reg_value = state[reg_idx]

                for threshold in thresholds:
                    if reg_value >= threshold:  # Example condition for increasing activity
                        if current_value < variables[gene]:  # Ensure we stay within bounds
                            new_state = list(state)
                            new_state[idx] += 1
                            successors.append(tuple(new_state))
                    if reg_value <= threshold:  # Example condition for decreasing activity
                        if current_value > 0:
                            new_state = list(state)
                            new_state[idx] -= 1
                            successors.append(tuple(new_state))

        if not successors:
            successors.append(state)
        return list(set(successors))  # Remove duplicate transitions

    # Add transitions to the graph
    for state in all_states:
        successors = generate_successors(state)
        for succ in successors:
            G.add_edge(state, succ)

    stg = StateTransitionGraph(None)
    stg.variables = variables
    stg.states = all_states
    stg.graph = G
    #parsed_formula = parse_formula("((x >= 5) & (x <= 12) & (y >= 4) & (y <= 10)) | (x >= 9) & (x <= 15) & (y >= 7) & (y <= 13)")
    parsed_formula = parse_formula(
       # "EG (((x >= 5) & (x <= 12) & (y >= 4) & (y <= 10)) | ((x >= 9) & (x <= 15) & (y >= 7) & (y <= 13)))")
        "AG !(x >= 2)")
    positive_formula = parsed_formula.eliminate_negation()
    #initial_states = generate_initial_states(json_data.get("initial_states"), json_data.get("network").get("variables"))
    ks = KripkeStructure(stg, None)
    formulae_evaluations = model_check(ks, positive_formula)
    format_result(formulae_evaluations, ks.init_states, positive_formula)


def main(json_file):
    """
    Main function to load data, parse formulas, validate states, generate states, build Kripke structure,
    perform model checking, and print results.

    @param json_file: Path to the JSON file containing input data
    """
    with open(json_file, 'r') as file:
        json_data = json.load(file)

    formula = json_data.get("formula")
    parsed_formula = parse_formula(formula)
    positive_formula = parsed_formula.eliminate_negation()
    network_data = json_data.get("network")
    mvgrn = MvGRNParser(network_data).parse()
    validate_initial_states(json_data.get("initial_states"), mvgrn)
    stg = StateTransitionGraph(mvgrn)
    initial_states = generate_initial_states(json_data.get("initial_states"), json_data.get("network").get("variables"))
    ks = KripkeStructure(stg, initial_states)
    formulae_evaluations = model_check(ks, positive_formula)
    format_result(formulae_evaluations, ks.init_states, positive_formula)


if __name__ == "__main__":
    json_file = "path_to_your_json_file.json"  # Update this path to your JSON file
    main2(json_file)
